# Frontend Implementation — Detailed Steps

> Backend base URL: `http://localhost:8000/api/v1`  
> All request/response shapes below are derived from the actual Pydantic schemas and route handlers in the `src/` directory.

---

## Phase 1 — Scaffold + Infrastructure
Scaffold + Infrastructure: Vite setup, dependencies, directory structure, TypeScript types (mirroring all Pydantic schemas), Axios instance with 401→refresh→retry interceptor (with concurrent request queuing), QueryClient, Zustand auth store with localStorage persistence, and wiring

### 1.1 Create the Vite project

```bash
npm create vite@latest bookly-frontend -- --template react-ts
cd bookly-frontend
npm install
npm run dev
```

### 1.2 Install core dependencies

```bash
npm install axios @tanstack/react-query zustand react-router-dom
```

```bash
npm install -D @types/react @types/react-dom
```

### 1.3 Install Tailwind CSS (optional, pending decision)

```bash
npm install -D tailwindcss @tailwindcss/vite
```

- Add `@import "tailwindcss";` to `src/index.css`
- Add the Tailwind plugin to `vite.config.ts`

### 1.4 Configure Vite environment variable

Create `bookly-frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Add a `bookly-frontend/src/vite-env.d.ts` declaration (Vite creates this by default) — no extra work needed; `import.meta.env.VITE_API_BASE_URL` is typed automatically.

### 1.5 Define the project directory structure

Create the following folders and placeholder files inside `bookly-frontend/src/`:

```
src/
  main.tsx                  # App entry — mounts <App /> inside QueryClientProvider + RouterProvider
  App.tsx                   # Root component — renders <Outlet /> from react-router
  types/
    index.ts                # All shared TypeScript interfaces
  lib/
    api.ts                  # Axios instance + request/response interceptors (refresh flow)
    queryClient.ts          # QueryClient factory
    errors.ts               # Normalized ApiError class + helper
  features/
    auth/
      authStore.ts          # Zustand store — user, tokens, login/logout actions
      useAuth.ts            # Thin hook wrapping Zustand selectors
      LoginPage.tsx
      SignupPage.tsx
      VerifyEmailPage.tsx
      ForgotPasswordPage.tsx
      ResetPasswordPage.tsx
      api.ts                # Auth-specific axios calls
      queries.ts            # useCurrentUser query
    books/
      BooksListPage.tsx
      BookDetailPage.tsx
      BookForm.tsx          # Shared create/edit form component
      api.ts                # Books axios calls
      queries.ts            # useBooks, useBook, useCreateBook, useUpdateBook, useDeleteBook
    reviews/
      ReviewList.tsx        # Renders reviews inside BookDetail
      ReviewForm.tsx        # Add-review form inside BookDetail
      api.ts                # Reviews axios calls
      queries.ts            # useAddReview, useDeleteReview
    tags/
      TagsListPage.tsx
      TagChips.tsx          # Renders tags on BookDetail + add/remove
      api.ts                # Tags axios calls
      queries.ts            # useTags, useCreateTag, useAddTagsToBook, useUpdateTag, useDeleteTag
  components/
    Layout.tsx              # NavBar + <Outlet />
    NavBar.tsx              # Links — conditional on auth state
    ProtectedRoute.tsx      # Redirects to /login if not authenticated
    Loading.tsx             # Spinner / skeleton
    ErrorMessage.tsx        # Renders ApiError.message
  router.tsx                # createBrowserRouter config
  test/
    setup.ts                # Vitest setup — import MSW server
    server.ts               # MSW handlers
    mocks/
      handlers.ts           # Per-feature mock handlers
```

### 1.6 Define shared TypeScript types (`src/types/index.ts`)

Mirror every Pydantic response schema. All fields must match the backend exactly.

```ts
// --- Users ---
export interface User {
  uid: string;               // uuid serialized as string
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  created_at: string;        // ISO datetime string
  updated_at: string;
  // password_hash is excluded by Field(exclude=True) — never sent to frontend
}

export interface UserCreateResponse {
  message: string;
  user: User;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  user: {
    user: string;            // email
    uid: string;
  };
}

export interface RefreshResponse {
  access_token: string;
}

// --- Books ---
export interface Tag {
  uid: string;
  name: string;
  created_at: string;
}

export interface Book {
  uid: string;
  title: string;
  author: string;
  publisher: string;
  page_count: number;
  language: string;
  published_date: string;    // "YYYY-MM-DD"
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export interface BookDetail extends Book {
  reviews: Review[];
}

export interface BookCreate {
  title: string;
  author: string;
  publisher: string;
  page_count: number;
  language: string;
  published_date?: string;   // defaults to "YYYY-MM-DD" on backend
}

export interface BookUpdate {
  title?: string;
  author?: string;
  publisher?: string;
  page_count?: number;
  language?: string;
  published_date?: string;
}

// --- Reviews ---
export interface Review {
  uid: string;
  rating: number;            // 1–5
  review_text: string;
  user_uid: string | null;
  book_uid: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreate {
  rating: number;
  review_text: string;
}

// --- Tags ---
export interface TagCreate {
  name: string;
}

export interface TagAdd {
  tags: TagCreate[];
}

// --- API Error shape (matches errors.py register_all_errors) ---
export interface ApiErrorPayload {
  message: string;
  resolution?: string;
  error_code: string;
}
```

### 1.7 Build the Axios instance with refresh interceptor (`src/lib/api.ts`)

**Key behaviors from `src/auth/routes.py`:**

| Endpoint | Method | Auth header needed | Response shape |
|---|---|---|---|
| `POST /auth/login` | POST | No | `{ message, access_token, refresh_token, user: { user, uid } }` |
| `GET /auth/refresh_token` | GET | Refresh token (header or cookie — depends on `RefreshTokenBearer`) | `{ access_token }` |
| `GET /auth/logout` | GET | Access token (Bearer header) | `{ message }` |

Implementation outline:

```ts
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../features/auth/authStore";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// --- Request interceptor: attach access_token ---
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- Response interceptor 402 -> refresh -> retry (queue concurrent 401s) ---
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (token: string | null, error: unknown) => {
  failedQueue.forEach((prom) => {
    if (error || !token) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Only attempt refresh on 401, and not on the refresh endpoint itself
    if (
      error.response?.status != 401 ||
      originalRequest._retry ||
      originalRequest.url === "/auth/refresh_token"
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const refreshToken = useAuthStore.getState().refreshToken;
      const { data } = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/auth/refresh_token`,
        {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
            "Content-Type": "application/json",
          },
        },
      );
      // With destructuring — pulling data straight out
      // The axios response object always has a data key,

      const newAccessToken: string = data.access_token;
      useAuthStore.getState().setAccessToken(newAccessToken);
      processQueue(newAccessToken, null);

      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(null, refreshError);
      //Refresh failed -> logout -> redirect
      useAuthStore.getState().logout();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export default api;

```

**Important detail:** The `RefreshTokenBearer` dependency in the backend reads the token from the `Authorization` header as a Bearer token. Confirm this by reading `src/auth/dependencies.py`. If it reads from a cookie or a custom header instead, adjust the refresh call accordingly.

### 1.8 Create the QueryClient factory (`src/lib/queryClient.ts`)

```ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,   // 1 minute
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

### 1.9 Create the normalized error helper (`src/lib/errors.ts`)

The backend error shape (from `errors.py`) is always:

```json
{
  "message": "string",
  "resolution": "string (optional)",
  "error_code": "string"
}
```

```ts
import axios from "axios";
import type { ApiErrorPayload } from "../types/apiErrorPayload";

export function parseApiError(error: unknown): ApiErrorPayload {
  if (axios.isAxiosError(error) && error.response) {
    const data = error.response.data; // typed as `any` by axios, but at least response.data is guaranteed to exist

    if (
      typeof data === "object" &&
      data !== null &&
      "message" in data &&
      "error_code" in data
    ) {
      return data as ApiErrorPayload;
    }
  }
  return {
    message: "An unexpected error occurred",
    error_code: "unknown",
  };
}
```

### 1.10 Build the Zustand auth store (`src/features/auth/authStore.ts`)

```ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "../../types";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setTokens: (access: string, refresh: string) => void;
  setAccessToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,

      setTokens: (access, refresh) =>
        set({ accessToken: access, refreshToken: refresh }),

      setAccessToken: (token) => set({ accessToken: token }),

      setUser: (user) => set({ user }),

      logout: () =>
        set({ accessToken: null, refreshToken: null, user: null }),

      isAuthenticated: () => get().accessToken !== null,
    }),
    {
      name: "bookly-auth",    // localStorage key
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);
```

### 1.11 Create the `useAuth` hook (`src/features/auth/useAuth.ts`)

```ts
import { useAuthStore } from "./authStore";

export function useAuth() {
  return {
    user: useAuthStore((s) => s.user),
    isAuthenticated: useAuthStore((s) => s.isAuthenticated),
    accessToken: useAuthStore((s) => s.accessToken),
  };
}
```

### 1.12 Wire up `main.tsx` and `App.tsx`

```tsx
// main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/queryClient.ts";
import { RouterProvider } from "react-router-dom";
import { router } from "./router.tsx";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
    {/* <App /> */}
  </StrictMode>,
);



```

```tsx
// App.tsx
import { Outlet } from "react-router-dom";

export default function App() {
  return <Outlet />;
}
```

### 1.13 Create `router.tsx` (initial — no routes yet)

```tsx
import { createBrowserRouter } from "react-router-dom";
import App from "./App";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      // Routes added in Phase 2
    ],
  },
]);
```

### 1.14 Verify the scaffold compiles

```bash
cd bookly-frontend && npx tsc --noEmit && npm run dev
```

Open browser at `http://localhost:5173` — should show the default Vite + React page with no errors in the terminal.

---

## Phase 2 — Auth Pages
Auth Pages: Login, Signup, Verify Email, Forgot/Reset Password, NavBar, ProtectedRoute, Layout — all with exact backend error shapes from errors.py


### 2.1 Build auth API helper (`src/features/auth/api.ts`)

Each function maps 1:1 to a backend route.

| Function | Backend route | Request body | Response |
|---|---|---|---|
| `signup(data)` | `POST /auth/signup` | `{ first_name, last_name, username, email, password }` | `{ message, user }` |
| `login(data)` | `POST /auth/login` | `{ email, password }` | `{ message, access_token, refresh_token, user: { user, uid } }` |
| `logout()` | `GET /auth/logout` | — | `{ message }` |
| `verifyEmail(token)` | `GET /auth/verify/{token}` | — | `{ message }` |
| `requestPasswordReset(data)` | `POST /auth/password-reset-request` | `{ email }` | `{ message }` |
| `resetPassword(token, data)` | `POST /auth/password-reset-confirm/{token}` | `{ new_password, confirm_new_password }` | `{ message }` |
| `getCurrentUser()` | `GET /auth/me` | — | Full `UserBooksOut` (user + books + reviews) |

```ts
import api from "../../../lib/api";
import type {
  User,
  UserCreateResponse,
  LoginResponse,
  Tag,
  Book,
  Review,
  ReviewCreate,
  TagCreate,
  TagAdd,
  BookCreate,
  BookUpdate,
} from "../../../types";

// Auth
export const signup = (data: {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
}) => api.post<UserCreateResponse>("/auth/signup", data);

export const login = (data: { email: string; password: string }) =>
  api.post<LoginResponse>("/auth/login", data);

export const logout = () => api.get("/auth/logout");

export const verifyEmail = (token: string) =>
  api.get(`/auth/verify/${token}`);

export const requestPasswordReset = (data: { email: string }) =>
  api.post("/auth/password-reset-request", data);

export const resetPassword = (
  token: string,
  data: { new_password: string; confirm_new_password: string }
) => api.post(`/auth/password-reset-confirm/${token}`, data);

export const getCurrentUser = () => api.get("/auth/me");
```

### 2.2 Create `useCurrentUser` query (`src/features/auth/queries.ts`)

```ts
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "./api";
import { useAuthStore } from "./authStore";

export function useCurrentUser() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const { data } = await getCurrentUser();
      return data;  // UserBooksOut
    },
    enabled: isAuthenticated(),
    staleTime: 5 * 60 * 1000,
  });
}
```

### 2.3 Build `<LoginPage />`

**File:** `src/features/auth/LoginPage.tsx`

- Render a form: email, password fields + submit button
- On submit call `login({ email, password })` from `api.ts`
- On success: `useAuthStore.getState().setTokens(accessToken, refreshToken)` → fetch `/auth/me` → `setUser(data)` → navigate to `/`
- On error: parse with `parseApiError(error)` → display via `<ErrorMessage />`
- Link to `/signup` and `/forgot-password`

**Backend validation notes:**
- `POST /auth/login` returns 400 with `{ message: "Invalid Email Or Password", error_code: "invalid_email_or_password" }` on bad credentials (from `InvalidCredentials` in `errors.py:71`)
- Rate limited: 10/minute per IP (SlowAPI)

### 2.4 Build `<SignupPage />`

**File:** `src/features/auth/SignupPage.tsx`

- Form fields: `first_name`, `last_name`, `username`, `email`, `password`, `confirm_password`
- Validate locally that `password === confirm_password` before sending (backend validates `new_password` match on reset, but not on signup)
- Validate `username.length <= 8` and `email.length <= 40` per Pydantic `Field(max_length=...)` in `UserCreate` schema
- Validate `password.length >= 6` per `PasswordStr = Annotated[str, Field(min_length=6)]`
- On submit: `signup({ first_name, last_name, username, email, password })`
- On success: show a "check your email" confirmation message, redirect to `/login`
- On error: 403 `{ message: "User with email already exists", error_code: "user_exists" }` → display

### 2.5 Build `<VerifyEmailPage />`

**File:** `src/features/auth/VerifyEmailPage.tsx`

- Read `token` from URL: `const { token } = useParams<{ token: string }>()`
- On mount, call `verifyEmail(token!)`
- Show loading state → then success/error message
- Link to `/login`

**Note:** Backend link format is `http://localhost:8000/api/v1/auth/verify/{token}` (raw JSON response). For Phase 2, this page will be triggered manually or by copying the token. Later (Phase 5) can repoint backend links to `http://localhost:5173/verify/{token}`.

### 2.6 Build `<ForgotPasswordPage />`

**File:** `src/features/auth/ForgotPasswordPage.tsx`

- Form: single email field
- On submit: `requestPasswordReset({ email })`
- Always show the same success message regardless of whether the email exists (backend does this intentionally for security — see `routes.py:214`)

### 2.7 Build `<ResetPasswordPage />`

**File:** `src/features/auth/ResetPasswordPage.tsx`

- Read `token` from URL params
- Form: `new_password`, `confirm_new_password`
- Client-side validation: passwords match, length >= 6
- On submit: `resetPassword(token, { new_password, confirm_new_password })`
- On success: navigate to `/login`
- On error: 401 invalid token, 404 user not found, 500 general error

### 2.8 Build shared components

**`<Loading />`** (`src/components/Loading.tsx`):
- Simple spinner or skeleton component
- Accept optional `fullPage` prop for centered full-page loading

**`<ErrorMessage />`** (`src/components/ErrorMessage.tsx`):
- Accept `error: unknown` prop
- Use `parseApiError(error)` to extract `message` and `error_code`
- Render in a styled div with the error message

**`<NavBar />`** (`src/components/NavBar.tsx`):
- If authenticated: show user email, "Books", "Logout" button
- If not authenticated: show "Login", "Signup" links
- Logout button calls `logout()` API → `useAuthStore.getState().logout()` → navigate to `/login`

**`<ProtectedRoute />`** (`src/components/ProtectedRoute.tsx`):
```tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return <Outlet />;
}
```

**`<Layout />`** (`src/components/Layout.tsx`):
```tsx
import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";

export default function Layout() {
  return (
    <div>
      <NavBar />
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

### 2.9 Update `router.tsx` with auth routes

```tsx
import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./features/auth/LoginPage";
import SignupPage from "./features/auth/SignupPage";
import VerifyEmailPage from "./features/auth/VerifyEmailPage";
import ForgotPasswordPage from "./features/auth/ForgotPasswordPage";
import ResetPasswordPage from "./features/auth/ResetPasswordPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { element: <Layout />, children: [
        { path: "login", element: <LoginPage /> },
        { path: "signup", element: <SignupPage /> },
        { path: "verify/:token", element: <VerifyEmailPage /> },
        { path: "forgot-password", element: <ForgotPasswordPage /> },
        { path: "reset-password/:token", element: <ResetPasswordPage /> },
        // Protected routes added in Phase 3
        { element: <ProtectedRoute />, children: [] },
      ]},
    ],
  },
]);
```

### 2.10 Manual smoke test for auth flow

1. Run backend: `fastapi dev src/` (port 8000)
2. Run frontend: `npm run dev` (port 5173)
3. Sign up → see "check email" message
4. Manually call verify endpoint (backend sends email via Celery, or hit the link directly)
5. Login → confirm `localStorage` has `bookly-auth` key with tokens + user
6. Refresh page → confirm tokens persist (Zustand `persist` middleware)
7. Navigate to `/` → confirm `<ProtectedRoute>` shows (or redirects to login if logged out)

---

## Phase 3 — Books CRUD
Books CRUD: typed API client, TanStack Query hooks with cache invalidation, BooksList, BookDetail, BookForm (shared create/edit)


### 3.1 Build books API helper (`src/features/books/api.ts`)

| Function | Backend route | Auth required | Request body | Response |
|---|---|---|---|---|
| `getBooks()` | `GET /books/` | Yes | — | `Book[]` |
| `getBook(uid)` | `GET /books/{uid}` | Yes | — | `BookDetail` |
| `createBook(data)` | `POST /books/` | Yes | `BookCreate` | `Book` |
| `updateBook(uid, data)` | `PATCH /books/{uid}` | Yes | `BookUpdate` | `Book` |
| `deleteBook(uid)` | `DELETE /books/{uid}` | Yes | — | 204 (empty) |

```ts
import api from "../../../lib/api";
import type { Book, BookDetail, BookCreate, BookUpdate } from "../../../types";

export const getBooks = () => api.get<Book[]>("/books/");

export const getBook = (uid: string) =>
  api.get<BookDetail>(`/books/${uid}`);

export const createBook = (data: BookCreate) =>
  api.post<Book>("/books/", data);

export const updateBook = (uid: string, data: BookUpdate) =>
  api.patch<Book>(`/books/${uid}`, data);

export const deleteBook = (uid: string) =>
  api.delete(`/books/${uid}`);   // returns 204
```

**Error shapes from `errors.py`:**
- `BookNotFound`: 404 `{ message: "Book not found", error_code: "book_not_found" }`
- `NotAuthenticated`: 401 `{ message: "User is not authenticated", error_code: "not_authenticated" }`
- `InvalidToken`: 401 `{ message: "Token is invalid Or expired", error_code: "invalid_token" }`

### 3.2 Create books queries/mutations (`src/features/books/queries.ts`)

```ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBooks, getBook, createBook, updateBook, deleteBook } from "./api";
import type { BookCreate, BookUpdate } from "../../types";

export const bookKeys = {
  all: ["books"] as const,
  detail: (uid: string) => ["books", uid] as const,
};

export const useBooks = () =>
  useQuery({
    queryKey: bookKeys.all,
    queryFn: async () => {
      const { data } = await getBooks();
      return data;
    },
  });

export const useBook = (uid: string) =>
  useQuery({
    queryKey: bookKeys.detail(uid),
    queryFn: async () => {
      const { data } = await getBook(uid);
      return data;
    },
    enabled: !!uid,
  });

export const useCreateBook = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: BookCreate) => createBook(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: bookKeys.all }),
  });
};

export const useUpdateBook = (uid: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: BookUpdate) => updateBook(uid, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bookKeys.all });
      qc.invalidateQueries({ queryKey: bookKeys.detail(uid) });
    },
  });
};

export const useDeleteBook = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (uid: string) => deleteBook(uid),
    onSuccess: () => qc.invalidateQueries({ queryKey: bookKeys.all }),
  });
};
```

### 3.3 Build `<BooksListPage />`

**File:** `src/features/books/BooksListPage.tsx`

- Use `useBooks()` query
- While loading: show `<Loading />`
- If error: show `<ErrorMessage />`
- If empty: show "No books yet. Add one!" message
- Render a grid/list of book cards, each linking to `/books/{uid}`
- Include a "Create Book" button linking to `/books/new`
- Book card shows: title, author, publisher, language, tag chips

### 3.4 Build `<BookForm />`

**File:** `src/features/books/BookForm.tsx`

- Accept optional `initialData?: BookUpdate` and `onSubmit` prop for reuse in create and edit modes
- Fields: `title`, `author`, `publisher`, `page_count` (number), `language`, `published_date` (date string, default `"YYYY-MM-DD"`)
- Client-side validation:
  - All fields required (matching backend Pydantic `BookBase`)
  - `page_count` must be a positive integer
  - `published_date` format: `YYYY-MM-DD` (backend accepts raw string, not validated as `date` type)
- On submit: call `useCreateBook().mutateAsync(data)` or `useUpdateBook(uid).mutateAsync(data)` depending on mode

**Backend note:** The `BookCreate` schema has `published_date: str = "YYYY-MM-DD"` — it accepts a plain string, not a validated date. The `BookUpdate` schema makes all fields optional.

### 3.5 Build `<BookDetailPage />`

**File:** `src/features/books/BookDetailPage.tsx`

- Read `uid` from `useParams()`
- Use `useBook(uid)` query
- Display: title, author, publisher, page_count, language, published_date
- Render `<TagChips bookUid={uid} tags={book.tags} />` section
- Render `<ReviewList reviews={book.reviews} />` section
- Render `<ReviewForm bookUid={uid} />` section
- Edit button → navigates to `/books/{uid}/edit` (or opens inline form)
- Delete button with confirmation dialog → `useDeleteBook().mutateAsync(uid)` → navigate to `/`

### 3.6 Build books routes in `router.tsx`

Add inside the `<ProtectedRoute>` children:

```tsx
import BooksListPage from "./features/books/BooksListPage";
import BookDetailPage from "./features/books/BookDetailPage";
import BookForm from "./features/books/BookForm";

// Inside ProtectedRoute children:
{ path: "books", element: <BooksListPage /> },
{ path: "books/new", element: <BookForm mode="create" /> },
{ path: "books/:uid", element: <BookDetailPage /> },
{ path: "books/:uid/edit", element: <BookForm mode="edit" /> },
```

### 3.7 Update NavBar to include Books link

Add "Books" link in `<NavBar />` when authenticated, pointing to `/books`.

---

## Phase 4 — Reviews + Tags
Reviews + Tags: add/delete reviews inline on BookDetail, TagChips with add/remove, full tag CRUD

### 4.1 Build reviews API helper (`src/features/reviews/api.ts`)

| Function | Backend route | Auth required | Request body | Response |
|---|---|---|---|---|
| `getReviews()` | `GET /reviews/` | Admin only | — | `Review[]` |
| `getReview(uid)` | `GET /reviews/{uid}` | User/Admin | — | `Review` |
| `addReview(bookUid, data)` | `POST /reviews/book/{book_uid}` | User/Admin | `ReviewCreate` | `Review` |
| `deleteReview(uid)` | `DELETE /reviews/{uid}` | User/Admin | — | 204 |

```ts
import api from "../../../lib/api";
import type { Review, ReviewCreate } from "../../../types";

export const getReviews = () => api.get<Review[]>("/reviews/");

export const getReview = (uid: string) =>
  api.get<Review>(`/reviews/${uid}`);

export const addReview = (bookUid: string, data: ReviewCreate) =>
  api.post<Review>(`/reviews/book/${bookUid}`, data);

export const deleteReview = (uid: string) =>
  api.delete(`/reviews/${uid}`);
```

**Error shapes:**
- `ReviewNotFound`: 404 `{ message: "Review Not Found", error_code: "review_not_found" }`
- `InsufficientPermission`: 401 `{ message: "You do not have enough permissions...", error_code: "insufficient_permissions" }`

### 4.2 Create reviews queries/mutations (`src/features/reviews/queries.ts`)

```ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addReview, deleteReview } from "./api";
import type { ReviewCreate } from "../../types";
import { bookKeys } from "../books/queries";

export const useAddReview = (bookUid: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ReviewCreate) => addReview(bookUid, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bookKeys.detail(bookUid) });
    },
  });
};

export const useDeleteReview = (bookUid: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reviewUid: string) => deleteReview(reviewUid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bookKeys.detail(bookUid) });
    },
  });
};
```

**Note:** Reviews are nested inside `BookDetailOut` (the `GET /books/{uid}` response includes `reviews: Review[]`). There is no standalone reviews list page for users — reviews are displayed inline on `<BookDetailPage />`. The `GET /reviews/` (admin-only) endpoint exists but is optional for Phase 4.

### 4.3 Build `<ReviewList />`

**File:** `src/features/reviews/ReviewList.tsx`

- Accept `reviews: Review[]` prop (from `BookDetail.reviews`)
- Render each review: rating (as stars or number), `review_text`, user UID, created_at
- If the current user owns the review (`user.uid === review.user_uid`), show a delete button
- Delete button: confirmation → `useDeleteReview(bookUid).mutateAsync(review.uid)`

### 4.4 Build `<ReviewForm />`

**File:** `src/features/reviews/ReviewForm.tsx`

- Accept `bookUid: string` prop
- Fields: `rating` (select 1–5, backend validates `Field(le=5)`), `review_text` (textarea)
- On submit: `useAddReview(bookUid).mutateAsync({ rating, review_text })`
- On success: clear form, review appears in list (via query invalidation)
- Show error via `<ErrorMessage />` if submission fails

### 4.5 Build tags API helper (`src/features/tags/api.ts`)

| Function | Backend route | Auth required | Request body | Response |
|---|---|---|---|---|
| `getTags()` | `GET /tags/` | User/Admin | — | `Tag[]` |
| `createTag(data)` | `POST /tags/` | User/Admin | `{ name }` | `Tag` |
| `addTagsToBook(bookUid, data)` | `POST /tags/book/{book_uid}/tags` | User/Admin | `{ tags: [{ name }] }` | `Book` |
| `updateTag(uid, data)` | `PUT /tags/{uid}` | User/Admin | `{ name }` | `Tag` |
| `deleteTag(uid)` | `DELETE /tags/{uid}` | User/Admin | — | 204 |

```ts
import api from "../../../lib/api";
import type { Tag, TagCreate, TagAdd, Book } from "../../../types";

export const getTags = () => api.get<Tag[]>("/tags/");

export const createTag = (data: TagCreate) =>
  api.post<Tag>("/tags/", data);

export const addTagsToBook = (bookUid: string, data: TagAdd) =>
  api.post<Book>(`/tags/book/${bookUid}/tags`, data);

export const updateTag = (uid: string, data: TagCreate) =>
  api.put<Tag>(`/tags/${uid}`, data);

export const deleteTag = (uid: string) =>
  api.delete(`/tags/${uid}`);
```

**Error shapes:**
- `TagNotFound`: 404 `{ message: "Tag Not Found", error_code: "tag_not_found" }`
- `TagAlreadyExists`: 403 `{ message: "Tag Already exists", error_code: "tag_exists" }`

### 4.6 Create tags queries/mutations (`src/features/tags/queries.ts`)

```ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTags, createTag, addTagsToBook, updateTag, deleteTag } from "./api";
import type { TagCreate, TagAdd } from "../../types";
import { bookKeys } from "../books/queries";

export const tagKeys = {
  all: ["tags"] as const,
};

export const useTags = () =>
  useQuery({
    queryKey: tagKeys.all,
    queryFn: async () => {
      const { data } = await getTags();
      return data;
    },
  });

export const useCreateTag = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TagCreate) => createTag(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: tagKeys.all }),
  });
};

export const useAddTagsToBook = (bookUid: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TagAdd) => addTagsToBook(bookUid, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bookKeys.detail(bookUid) });
      qc.invalidateQueries({ queryKey: bookKeys.all });
    },
  });
};

export const useUpdateTag = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ uid, data }: { uid: string; data: TagCreate }) =>
      updateTag(uid, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: tagKeys.all }),
  });
};

export const useDeleteTag = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (uid: string) => deleteTag(uid),
    onSuccess: () => qc.invalidateQueries({ queryKey: tagKeys.all }),
  });
};
```

### 4.7 Build `<TagChips />`

**File:** `src/features/tags/TagChips.tsx`

- Accept `bookUid: string` and `tags: Tag[]` props
- Render each tag as a chip/badge with its name
- Include an "Add Tag" button that opens a small inline form:
  - Input field for tag name
  - Submit calls `useAddTagsToBook(bookUid).mutateAsync({ tags: [{ name }] })`
  - If tag already exists on the book, backend handles deduplication via the many-to-many join
- Each chip has an "x" remove button → call `deleteTag(uid)` or `addTagsToBook` with remaining tags

### 4.8 Build `<TagsListPage />` (optional admin page)

**File:** `src/features/tags/TagsListPage.tsx`

- Use `useTags()` query to list all tags
- Each tag shows name + edit/delete buttons
- Edit: inline form calling `useUpdateTag().mutateAsync({ uid, data: { name } })`
- Delete: confirmation → `useDeleteTag().mutateAsync(uid)`
- "Create Tag" form at the top

### 4.9 Update router for tags routes (optional)

```tsx
{ path: "tags", element: <TagsListPage /> },
```

---

## Phase 5 — Polish + Tests
Polish + Tests: loading/empty states, error boundary, MSW setup + handlers, sample Vitest+RTL tests for auth store and components, type-check and lint commands, README


### 5.1 Loading and empty states

Audit every page and component:

| Component | Loading state | Empty state |
|---|---|---|
| `BooksListPage` | `<Loading fullPage />` skeleton grid | "No books yet. Create your first book!" with CTA |
| `BookDetailPage` | `<Loading fullPage />` skeleton | `<ErrorMessage />` (404) |
| `ReviewList` | Inline spinner | "No reviews yet. Be the first!" |
| `TagChips` | Inline dots | "No tags" (plain text) |
| `TagsListPage` | `<Loading />` | "No tags created yet" |

### 5.2 Form validation polish

- Add inline validation messages below each field (red text)
- Disable submit button while mutation is pending (`isPending` from `useMutation`)
- Show success toast or inline message after create/update/delete

### 5.3 Error boundary

Create `src/components/ErrorBoundary.tsx`:

```tsx
import React from "react";
import { useRouteError } from "react-router-dom";

export default function ErrorBoundary() {
  const error = useRouteError();
  return (
    <div>
      <h2>Something went wrong</h2>
      <pre>{JSON.stringify(error, null, 2)}</pre>
    </div>
  );
}
```

Add `errorElement: <ErrorBoundary />` to the root route in `router.tsx`.

### 5.4 Optimistic updates (optional enhancement)

For `useDeleteBook` and `useDeleteReview`, consider `onMutate` to immediately remove the item from the cached list before the server confirms. Example pattern:

```ts
onMutate: async (uid) => {
  await qc.cancelQueries({ queryKey: bookKeys.all });
  const previous = qc.getQueryData(bookKeys.all);
  qc.setQueryData(bookKeys.all, (old) =>
    (old as Book[]).filter((b) => b.uid !== uid)
  );
  return { previous };
},
onError: (_err, _uid, context) => {
  qc.setQueryData(bookKeys.all, context?.previous);
},
```

### 5.5 Vitest + React Testing Library setup

**Install testing dependencies:**

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event msw jsdom
```

**Configure Vitest in `vite.config.ts`:**

```ts
/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    css: true,
  },
});
```

**Create MSW setup (`src/test/setup.ts`):**

```ts
import "@testing-library/jest-dom";
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### 5.6 Write MSW handlers (`src/test/mocks/handlers.ts`)

```ts
import { http, HttpResponse } from "msw";
import type { LoginResponse, Book, BookDetail } from "../../types";

const BASE = "http://localhost:8000/api/v1";

export const handlers = [
  http.post(`${BASE}/auth/login`, async () => {
    const body: LoginResponse = {
      message: "Login successful",
      access_token: "mock-access-token",
      refresh_token: "mock-refresh-token",
      user: { user: "test@example.com", uid: "test-uid" },
    };
    return HttpResponse.json(body);
  }),

  http.get(`${BASE}/auth/me`, () => {
    return HttpResponse.json({
      uid: "test-uid",
      username: "testuser",
      email: "test@example.com",
      first_name: "Test",
      last_name: "User",
      is_verified: true,
      created_at: "2024-01-01T00:00:00",
      updated_at: "2024-01-01T00:00:00",
      books: [],
      reviews: [],
    });
  }),

  http.get(`${BASE}/books/`, () => {
    const books: Book[] = [
      {
        uid: "book-1",
        title: "The Great Gatsby",
        author: "F. Scott Fitzgerald",
        publisher: "Scribner",
        page_count: 180,
        language: "English",
        published_date: "1925-04-10",
        tags: [],
        created_at: "2024-01-01T00:00:00",
        updated_at: "2024-01-01T00:00:00",
      },
    ];
    return HttpResponse.json(books);
  }),

  // Add more handlers per feature as needed
];
```

### 5.7 Write sample test: auth store

**File:** `src/features/auth/__tests__/authStore.test.ts`

```ts
import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore } from "../authStore";

describe("authStore", () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
    localStorage.clear();
  });

  it("starts unauthenticated", () => {
    expect(useAuthStore.getState().isAuthenticated()).toBe(false);
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it("sets tokens and marks as authenticated", () => {
    useAuthStore.getState().setTokens("access-123", "refresh-456");
    expect(useAuthStore.getState().isAuthenticated()).toBe(true);
    expect(useAuthStore.getState().accessToken).toBe("access-123");
    expect(useAuthStore.getState().refreshToken).toBe("refresh-456");
  });

  it("persists to localStorage", () => {
    useAuthStore.getState().setTokens("access-123", "refresh-456");
    const stored = JSON.parse(localStorage.getItem("bookly-auth")!);
    expect(stored.state.accessToken).toBe("access-123");
  });

  it("clears state on logout", () => {
    useAuthStore.getState().setTokens("a", "b");
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().isAuthenticated()).toBe(false);
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
```

### 5.8 Write sample test: LoginPage component

**File:** `src/features/auth/__tests__/LoginPage.test.tsx`

```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../../lib/queryClient";
import LoginPage from "../LoginPage";

const renderWithProviders = (ui: React.ReactElement) =>
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("renders login button", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
  });

  it("renders link to signup", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByText(/sign up/i)).toHaveAttribute("href", "/signup");
  });
});
```

### 5.9 Write sample test: BooksListPage with MSW

**File:** `src/features/books/__tests__/BooksListPage.test.tsx`

```tsx
import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../../lib/queryClient";
import BooksListPage from "../BooksListPage";

const renderWithProviders = (ui: React.ReactElement) =>
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );

describe("BooksListPage", () => {
  it("renders books from API", async () => {
    renderWithProviders(<BooksListPage />);
    await waitFor(() => {
      expect(screen.getByText("The Great Gatsby")).toBeInTheDocument();
    });
  });
});
```

### 5.10 Run all tests

```bash
cd bookly-frontend && npx vitest run
```

Confirm all tests pass with no type errors.

### 5.11 Type-check the entire project

```bash
cd bookly-frontend && npx tsc --noEmit
```

Fix any type errors. Common issues:
- Missing `key` prop on mapped elements
- Non-null assertions on `useParams()` values
- `AxiosResponse` unwrapping (`data` property)

### 5.12 Update `frontend/README.md`

Document:
- Project name and description
- Tech stack (Vite, React, TypeScript, TanStack Query, Zustand, Axios, React Router)
- Setup instructions (`npm install`, `.env` configuration, `npm run dev`)
- Auth flow diagram (login → token storage → interceptor refresh → logout)
- API endpoints covered
- Testing instructions (`npm test`)
- Screenshot placeholder

### 5.13 Lint check (if ESLint is configured)

```bash
cd bookly-frontend && npx eslint src/
```

Fix any linting warnings. Vite's `react-ts` template comes with ESLint pre-configured.

---

## Cross-cutting concerns

### Backend email link repointing

Currently, the backend sends email links pointing to `http://localhost:8000/api/v1/auth/verify/{token}` (raw JSON). To redirect to the frontend:

1. **Option A (recommended for now):** Keep backend links as-is; user copies token manually to frontend URL `/verify/{token}`
2. **Option B (later):** Change `src/auth/routes.py:64` and `src/auth/routes.py:227` to point to `http://localhost:5173/verify/{token}` and `http://localhost:5173/reset-password/{token}` respectively

### CORS

Backend already has CORS set to `*` (confirmed in `src/middleware.py`), so no backend changes needed for dev.

### Environment variable reference

| Variable | Where | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `bookly-frontend/.env` | Base URL for all API calls |
| `JWT_SECRET`, `JWT_ALGORITHM`, etc. | Backend `.env` | Not exposed to frontend |
