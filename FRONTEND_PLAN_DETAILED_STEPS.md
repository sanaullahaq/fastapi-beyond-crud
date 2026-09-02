# Frontend Implementation — Detailed Steps

<details>
<summary>Table of Contents</summary>

- [Phase 1 — Scaffold + Infrastructure](#phase-1--scaffold--infrastructure)
  - [1.1 Create the Vite project](#11-create-the-vite-project)
  - [1.2 Install core dependencies](#12-install-core-dependencies)
  - [1.3 Install Tailwind CSS (DECIDED: CONFIRMED — installed)](#13-install-tailwind-css-decided-confirmed--installed)
  - [1.4 Configure Vite environment variable](#14-configure-vite-environment-variable)
  - [1.5 Define the project directory structure](#15-define-the-project-directory-structure)
  - [1.6 Shared TypeScript types (`src/types/*.ts` — implemented, per-domain files)](#16-shared-typescript-types-srctypests--implemented-per-domain-files)
  - [1.7 Build the Axios instance with refresh interceptor (`src/lib/apiClient.ts`)](#17-build-the-axios-instance-with-refresh-interceptor-srclibapiclientts)
  - [1.8 Create the QueryClient factory (`src/lib/queryClient.ts`)](#18-create-the-queryclient-factory-srclibqueryclientts)
  - [1.9 Create the normalized error helper (`src/lib/errors.ts`)](#19-create-the-normalized-error-helper-srcliberrorsts)
  - [1.10 Build the Zustand auth store (`src/features/auth/authStore.ts`)](#110-build-the-zustand-auth-store-srcfeaturesauthauthstorets)
  - [1.11 Create the `useAuth` hook (`src/features/auth/useAuth.ts`)](#111-create-the-useauth-hook-srcfeaturesauthuseauthts)
  - [1.12 Wire up `main.tsx` and `App.tsx`](#112-wire-up-maintsx-and-apptsx)
  - [1.13 Create `router.tsx` (initial — no routes yet)](#113-create-routertsx-initial--no-routes-yet)
  - [1.14 Verify the scaffold compiles](#114-verify-the-scaffold-compiles)
- [Phase 2 — Auth Pages](#phase-2--auth-pages)
  - [2.1 Build auth API helper (`src/features/auth/api.ts`)](#21-build-auth-api-helper-srcfeaturesauthapits)
  - [2.2 Create `useCurrentUser` query (`src/features/auth/queries.ts`)](#22-create-usecurrentuser-query-srcfeaturesauthqueriests)
  - [2.3 Build `<LoginPage />` — DETAILED SPEC (approved, ready to implement)](#23-build-loginpage---detailed-spec-approved-ready-to-implement)
    - [2.3.0 Prerequisite cleanup — `src/index.css`](#230-prerequisite-cleanup--srcindexcss)
    - [2.3.1 `<ErrorMessage />` (`src/components/ErrorMessage.tsx`)](#231-errormessage--srccomponentserrormessagetsx)
    - [2.3.2 `<LoginPage />` (`src/features/auth/LoginPage.tsx`)](#232-loginpage--srcfeaturesauthloginpagetsx)
    - [2.3.3 Register the route (`src/router.tsx`)](#233-register-the-route-srcroutertsx)
    - [2.3.4 Backend behavior notes](#234-backend-behavior-notes)
    - [2.3.5 Verification](#235-verification)
  - [2.4 Build `<SignupPage />` — DETAILED SPEC (approved, ready to implement)](#24-build-signuppage---detailed-spec-approved-ready-to-implement)
    - [2.4.1 Backend contract (verified against `src/auth/schemas.py`)](#241-backend-contract-verified-against-srcauthschemaspy)
    - [2.4.2 Form & validation strategy](#242-form--validation-strategy)
    - [2.4.3 Flow](#243-flow)
    - [2.4.4 Full implementation (`src/features/auth/SignupPage.tsx`)](#244-full-implementation-srcfeaturesauthsignuppagetsx)
    - [2.4.5 Styling & conventions](#245-styling--conventions)
    - [2.4.6 Verification](#246-verification)
  - [2.5 Build `<VerifyEmailPage />` — DETAILED SPEC](#25-build-verifyemailpage---detailed-spec)
    - [2.5.1 Backend contract (from `src/auth/routes.py:86-107`)](#251-backend-contract-from-srcauthroutespy86-107)
    - [2.5.2 Design decisions](#252-design-decisions)
    - [2.5.3 Full implementation (`src/features/auth/VerifyEmailPage.tsx`)](#253-full-implementation-srcfeaturesauthverifyemailpagetsx)
    - [2.5.4 Router update (`src/router.tsx`)](#254-router-update-srcroutertsx)
    - [2.5.5 Verification](#255-verification)
  - [2.6 Build `<PasswordResetRequestPage />` — DETAILED SPEC](#26-build-passwordresetrequestpage---detailed-spec)
    - [2.6.1 Backend contract (from `src/auth/routes.py:209-248`)](#261-backend-contract-from-srcauthroutespy209-248)
    - [2.6.2 Design decisions](#262-design-decisions)
    - [2.6.3 Full implementation (`src/features/auth/PasswordResetRequestPage.tsx`)](#263-full-implementation-srcfeaturesauthpasswordresetrequestpagetsx)
    - [2.6.4 Router registration (`src/router.tsx`)](#264-router-registration-srcroutertsx)
    - [2.6.5 Verification](#265-verification)
  - [2.7 Build `<ResetAccountPassword />` — DETAILED SPEC](#27-build-resetaccountpassword---detailed-spec)
    - [2.7.1 Backend contract (from `src/auth/routes.py:251-288`, `src/auth/schemas.py:88-94`)](#271-backend-contract-from-srcauthroutespy251-288-srcauthschemaspy88-94)
    - [2.7.2 Design decisions](#272-design-decisions)
    - [2.7.3 Full implementation (`src/features/auth/ResetAccountPassword.tsx`)](#273-full-implementation-srcfeaturesauthresetaccountpasswordtsx)
    - [2.7.4 Router registration (`src/router.tsx`)](#274-router-registration-srcroutertsx)
    - [2.7.5 Verification](#275-verification)
  - [2.8 Build shared components — DETAILED SPEC](#28-build-shared-components--detailed-spec)
    - [2.8.1 `<ErrorMessage />` — already exists, reference only](#281-errormessage---already-exists-reference-only)
    - [2.8.2 `<Loading />` — spinner](#282-loading---spinner)
    - [2.8.3 `<NavBar />` — top nav, conditional on auth](#283-navbar---top-nav-conditional-on-auth)
    - [2.8.4 `<ProtectedRoute />` — redirect if not authenticated](#284-protectedroute---redirect-if-not-authenticated)
    - [2.8.5 `<Layout />` — NavBar + routed content](#285-layout---navbar--routed-content)
    - [2.8.6 Wiring — `Layout` mounted via `App.tsx`](#286-wiring--layout-mounted-via-apptsx)
    - [2.8.7 Verification](#287-verification)
  - [2.9 Update `router.tsx` with auth routes](#29-update-routertsx-with-auth-routes)
  - [2.10 Manual smoke test for auth flow](#210-manual-smoke-test-for-auth-flow)
- [Phase 3 — Books CRUD](#phase-3--books-crud)
  - [3.1 Build books API helper (`src/features/books/api.ts`) — DETAILED SPEC](#31-build-books-api-helper-srcfeaturesbooksapits--detailed-spec)
  - [3.2 Create books queries/mutations (`src/features/books/queries.ts`) — DETAILED SPEC](#32-create-books-queriesmutations-srcfeaturesbooksqueriests--detailed-spec)
  - [3.3 Build `<BooksListPage />` — DETAILED SPEC](#33-build-bookslistpage---detailed-spec)
  - [3.4 Build `<BookForm />` — DETAILED SPEC](#34-build-bookform---detailed-spec)
  - [3.5 Build `<ConfirmDialog />` + `<BookDetailPage />` — DETAILED SPEC](#35-build-confirmdialog---bookdetailpage---detailed-spec)
    - [3.5.1 `<ConfirmDialog />` (reusable shared component)](#351-confirmdialog--reusable-shared-component)
    - [3.5.2 `<BookDetailPage />`](#352-bookdetailpage-)
  - [3.6 Restructure `router.tsx` — mount `<ProtectedRoute />` + books routes — DETAILED SPEC](#36-restructure-routertsx--mount-protectedroute---books-routes--detailed-spec)
  - [3.7 NavBar "Books" link — reconciliation note](#37-navbar-books-link--reconciliation-note)
  - [3.8 Verification — DETAILED SPEC](#38-verification--detailed-spec)
- [Phase 4 — Reviews + Tags](#phase-4--reviews--tags)
  - [4.1 Build reviews API helper (`src/features/reviews/api.ts`)](#41-build-reviews-api-helper-srcfeaturesreviewsapits)
  - [4.2 Create reviews queries/mutations (`src/features/reviews/queries.ts`)](#42-create-reviews-queriesmutations-srcfeaturesreviewsqueriests)
  - [4.3 Build `<ReviewList />`](#43-build-reviewlist-)
  - [4.4 Build `<ReviewForm />`](#44-build-reviewform-)
  - [4.5 Build tags API helper (`src/features/tags/api.ts`)](#45-build-tags-api-helper-srcfeaturestagsapits)
  - [4.6 Create tags queries/mutations (`src/features/tags/queries.ts`)](#46-create-tags-queriesmutations-srcfeaturestagsqueriests)
  - [4.7 Build `<TagChips />`](#47-build-tagchips-)
  - [4.8 Build `<TagsListPage />` (optional admin page)](#48-build-tagslistpage--optional-admin-page)
  - [4.9 Update router for tags routes (optional)](#49-update-router-for-tags-routes-optional)
- [Phase 5 — Polish + Tests](#phase-5--polish--tests)
  - [5.1 Loading and empty states](#51-loading-and-empty-states)
  - [5.2 Form validation polish](#52-form-validation-polish)
  - [5.3 Error boundary](#53-error-boundary)
  - [5.4 Optimistic updates (optional enhancement)](#54-optimistic-updates-optional-enhancement)
  - [5.5 Vitest + React Testing Library setup](#55-vitest--react-testing-library-setup)
  - [5.6 Write MSW handlers (`src/test/mocks/handlers.ts`)](#56-write-msw-handlers-srctestmockshandlersts)
  - [5.7 Write sample test: auth store](#57-write-sample-test-auth-store)
  - [5.8 Write sample test: LoginPage component](#58-write-sample-test-loginpage-component)
  - [5.9 Write sample test: BooksListPage with MSW](#59-write-sample-test-bookslistpage-with-msw)
  - [5.10 Run all tests](#510-run-all-tests)
  - [5.11 Type-check the entire project](#511-type-check-the-entire-project)
  - [5.12 Update `frontend/README.md`](#512-update-frontendreadmemd)
  - [5.13 Lint check (if ESLint is configured)](#513-lint-check-if-eslint-is-configured)
- [Cross-cutting concerns](#cross-cutting-concerns)
  - [Backend email link repointing](#backend-email-link-repointing)
  - [CORS](#cors)
  - [Environment variable reference](#environment-variable-reference)

</details>

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

### 1.3 Install Tailwind CSS (DECIDED: CONFIRMED — installed)

```bash
npm install -D tailwindcss @tailwindcss/vite
```

- Done: `@import "tailwindcss";` added to `src/index.css`
- Done: `@tailwindcss/vite` plugin added to `vite.config.ts` (`plugins: [react(), tailwindcss()]`)
- Required follow-up: strip all legacy Vite template styles from `src/index.css` — the scaffold still ships `#root { width: 1126px; text-align: center; border-inline: ... }`, hero CSS vars and dark-scheme overrides, which constrain width and fight Tailwind utilities. After cleanup, `index.css` contains only `@import "tailwindcss";` (executed as part of step 2.3).

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
  App.tsx                   # Root component — renders <Layout /> (NavBar + <Outlet />)
  types/
    users.ts                # UserOut, auth payloads (UserCreate, UserLogin, LoginResponse, UserDetailOut, ...)
    books.ts                # BookBase/BookCreate/BookUpdate/BookOut/BookDetailOut
    reviews.ts              # ReviewBase/ReviewCreate/ReviewOut
    tags.ts                 # TagOut/TagCreate/TagAdd
    apiErrorPayload.ts      # Backend error shape { message, resolution?, error_code }
  lib/
    apiClient.ts            # Axios instance + request/response interceptors (refresh flow)
    queryClient.ts          # QueryClient factory
    errors.ts               # Normalized ApiError class + helper
  features/
    auth/
      authStore.ts          # Zustand store — user, tokens, login/logout actions
      useAuth.ts            # Thin hook wrapping Zustand selectors
      LoginPage.tsx
      SignupPage.tsx
      VerifyEmailPage.tsx
      PasswordResetRequestPage.tsx   # Forgot-password (single email field)
      ResetAccountPassword.tsx       # Reset-password (two fields + token)
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
    Loading.tsx             # Spinner (Loader2), optional fullPage overlay
    ErrorMessage.tsx        # Renders ApiError.message
    ConfirmDialog.tsx       # Reusable inline confirm modal (Phase 3 §3.5)
  router.tsx                # createBrowserRouter config
  test/
    setup.ts                # Vitest setup — import MSW server
    server.ts               # MSW handlers
    mocks/
      handlers.ts           # Per-feature mock handlers
```

### 1.6 Shared TypeScript types (`src/types/*.ts` — implemented, per-domain files)

Types live in five domain files mirroring the Pydantic schemas. Conventions: `*Out` = response shapes, `*Create`/`*Update` = request bodies. All fields must match the backend exactly.

**`src/types/users.ts`:**

```ts
import type { BookOut } from "./books";
import type { ReviewOut } from "./reviews";

// --- Users ---
export interface UserOut {
  uid: string; // uuid serialized as string
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  created_at: string; // ISO datetime string
  updated_at: string;
  // password_hash is excluded by Field(exclude=True) — never sent to frontend
}

export interface UserCreateResponse {
  message: string;
  user: UserOut;
}

export interface UserCreate {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  refresh_token: string;
  user: {
    user: string; // email
    uid: string;
  };
}

export interface RefreshResponse {
  access_token: string;
}

export interface UserDetailOut extends UserOut {
  books: BookOut[];
  reviews: ReviewOut[];
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  new_password: string;
  confirm_new_password: string;
}
```

**`src/types/books.ts`:**

```ts
import type { ReviewOut } from "./reviews";
import type { TagOut } from "./tags";

// --- Books ---

export interface BookBase {
  title: string;
  author: string;
  publisher: string;
  page_count: number;
  language: string;
}

export interface BookCreate extends BookBase {
  published_date: string;
}

export interface BookUpdate {
  title?: string;
  author?: string;
  publisher?: string;
  page_count?: number;
  language?: string;
  published_date?: string;
}

export interface BookOut extends BookBase {
  uid: string;
  published_date: string; // "YYYY-MM-DD"
  tags: TagOut[];
  created_at: string;
  updated_at: string;
}

export interface BookDetailOut extends BookOut {
  reviews: ReviewOut[];
  tags: TagOut[];
}
```

**`src/types/reviews.ts`:**

```ts
// --- Reviews ---

export interface ReviewBase {
  rating: number;            // 1–5 (backend validates Field(le=5), ge=1)
  review_text: string;
}

export interface ReviewOut extends ReviewBase {
  uid: string;
  user_uid: string | null;
  book_uid: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreate extends ReviewBase {}
```

**`src/types/tags.ts`:**

```ts
// --- Tags ---

export interface TagOut {
  uid: string;
  name: string;
  created_at: string;
}

export interface TagCreate {
  name: string;
}

export interface TagAdd {
  tags: TagCreate[];
}
```

**`src/types/apiErrorPayload.ts`:**

```ts
// --- API Error shape (matches errors.py register_all_errors) ---
export interface ApiErrorPayload {
  message: string;
  resolution?: string;
  error_code: string;
}
```

Dependency graph: `users.ts` → `books.ts`, `reviews.ts`; `books.ts` → `reviews.ts`, `tags.ts`.

### 1.7 Build the Axios instance with refresh interceptor (`src/lib/apiClient.ts`)

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

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// --- Request interceptor: attach access_token ---
apiClient.interceptors.request.use((config) => {
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

apiClient.interceptors.response.use(
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
        return apiClient(originalRequest);
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
      return apiClient(originalRequest);
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

export default apiClient;

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
import type { UserOut } from "../../types/users";
import { queryClient } from "../../lib/queryClient";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserOut | null;
  setTokens: (access: string, refresh: string) => void;
  setAccessToken: (token: string) => void;
  setUser: (user: UserOut) => void;
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

      logout: () => {
        queryClient.removeQueries({ queryKey: ["currentUser"] });
        // drop every cached ["currentUser", ...] slot on logout — prevents
        // stale-cache-after-login-of-another-user (see §2.2 cache-invalidation note)
        set({ accessToken: null, refreshToken: null, user: null });
      },

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
import Layout from "./components/Layout";

export default function App() {
  return <Layout />;
}
```

> Updated in §2.8.6: `App` now renders `<Layout />` (NavBar + `<Outlet />`) instead of the bare `<Outlet />`, once the shared components exist.

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

Each function maps 1:1 to a backend route. All paths are rooted at a single `const PREFIX = "auth"` and interpolated into each template literal, so the version string lives in one place per feature.

| Function | Backend route | Request body | Response |
|---|---|---|---|
| `signup(data)` | `POST /auth/signup` | `{ first_name, last_name, username, email, password }` | `{ message, user }` |
| `login(data)` | `POST /auth/login` | `{ email, password }` | `{ message, access_token, refresh_token, user: { user, uid } }` |
| `logout()` | `GET /auth/logout` | — | `{ message }` |
| `verifyEmail(token)` | `GET /auth/verify/{token}` | — | `{ message }` |
| `requestPasswordReset(data)` | `POST /auth/password-reset-request` | `{ email }` | `{ message }` |
| `resetPassword(token, data)` | `POST /auth/password-reset-confirm/{token}` | `{ new_password, confirm_new_password }` | `{ message }` |
| `getCurrentUser()` | `GET /auth/me` | — | Full `UserDetailOut` (user + books + reviews) |

```ts
import apiClient from "../../lib/apiClient";
import type {
  UserCreateResponse,
  UserCreate,
  LoginResponse,
  UserDetailOut,
  PasswordResetRequest,
  PasswordResetConfirm,
  UserLogin,
} from "../../types/users";

const PREFIX = "auth";

// Auth
export const signup = (data: UserCreate) =>
  apiClient.post<UserCreateResponse>(`/${PREFIX}/signup`, data);

export const login = (data: UserLogin) =>
  apiClient.post<LoginResponse>(`/${PREFIX}/login`, data);

export const logout = () => apiClient.get(`/${PREFIX}/logout`);

export const verifyEmail = (token: string) =>
  apiClient.get(`/${PREFIX}/verify/${token}`);

export const requestPasswordReset = (data: PasswordResetRequest) =>
  apiClient.post(`/${PREFIX}/password-reset-request`, data);

export const resetPassword = (token: string, data: PasswordResetConfirm) =>
  apiClient.post(`/${PREFIX}/password-reset-confirm/${token}`, data);

export const getCurrentUser = () =>
  apiClient.get<UserDetailOut>(`/${PREFIX}/me`);
```
- `PREFIX = "auth"` has **no leading or trailing slash**; each call site adds its own slashes (`` `/${PREFIX}/signup` → `/auth/signup` ``). This is the shared pattern across every feature API module (see §3.1 for `books`).

### 2.2 Create `useCurrentUser` query (`src/features/auth/queries.ts`)

The query is **keyed on the access token** so each auth session has its own cache slot — this is what prevents "stale cache after logging in as a different user" (see cache-invalidation note below).

```ts
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "./authStore";
import { getCurrentUser } from "./api";

export function useCurrentUser() {
  const accessToken = useAuthStore((s) => s.accessToken); // primitive — identity changes on login/logout
  return useQuery({
    queryKey: ["currentUser", accessToken], // token-scoped: identity changes on login/logout
    queryFn: async () => {
      const { data } = await getCurrentUser();
      return data; // UserDetailOut
    },
    enabled: !!accessToken,
    staleTime: 5 * 60 * 1000,
  });
}
```

Design notes:
- `queryKey: ["currentUser", accessToken]` — the token is part of the cache identity. `["currentUser"]` is a **prefix**: `invalidateQueries({ queryKey: ["currentUser"] })` matches every token-scoped variant without needing to know the token. Logging in as a different user changes `accessToken`, so it becomes a **different cache slot** — no stale `UserDetailOut` from the previous user is served.
- `enabled: !!accessToken` — the query only runs when there is a logged-in token; while `false` it stays idle (no request, no error). Other components calling this hook share the one cached result (same key) and get instant cache hits on remount.
- `staleTime: 5 min` — overrides the global 1-min default: after fetching `/auth/me` the cache is fresh for 5 minutes; remounts within that window serve cache with **no** network call. `refetchOnWindowFocus: false` is set globally, so no refetch on focus either.

**Cache invalidation on logout** (ties into §1.10): `authStore.logout()` calls `queryClient.removeQueries({ queryKey: ["currentUser"] })`, which prefix-matches and **drops** every cached `["currentUser", ...]` entry. `removeQueries` (not `invalidateQueries`) is intentional — on logout we want the data *gone*, not refetched for the now-logged-out token.

### 2.3 Build `<LoginPage />` — DETAILED SPEC (approved, ready to implement)

**Files touched:**

| File | Action |
|---|---|
| `src/index.css` | Modify — strip legacy Vite template styles (see 1.3) |
| `src/components/ErrorMessage.tsx` | Create — shared error banner (pulled forward from 2.8) |
| `src/features/auth/LoginPage.tsx` | Create |
| `src/router.tsx` | Modify — register public `/login` route |

#### 2.3.0 Prerequisite cleanup — `src/index.css`

Replace the entire file with:

```css
@import "tailwindcss";
```

Why: leftover template styles (`#root { width: 1126px; max-width: 100%; text-align: center; border-inline: ... }`, hero vars, dark-scheme overrides) constrain layout and conflict with Tailwind on every future page.

#### 2.3.1 `<ErrorMessage />` (`src/components/ErrorMessage.tsx`)

Pulled forward from 2.8 because LoginPage (and every later page) depends on it:

```tsx
import { parseApiError } from "../lib/error";

export default function ErrorMessage({ error }: { error: unknown }) {
  const { message, resolution } = parseApiError(error);

  return (
    <div role="alert" className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
      <p>{message}</p>
      {resolution && <p className="mt-1 text-red-600">{resolution}</p>}
    </div>
  );
}
```

Matches backend payloads `{ message, resolution?, error_code }`.

#### 2.3.2 `<LoginPage />` (`src/features/auth/LoginPage.tsx`)

Key decisions:
- One `useMutation` wraps the whole success chain so `isPending` spans both network calls:
  1. `login()` → tokens
  2. `useAuthStore.getState().setTokens(...)` (persist middleware auto-writes localStorage key `bookly-auth`)
  3. `getCurrentUser()` (`/auth/me`) → `setUser(data)`
  4. `onSuccess:` → `navigate("/", { replace: true })`
- Controlled inputs + HTML5 validation (`type="email"`, `required`) — no form library needed
- UX polish: show/hide password toggle, submit disabled + relabeled while pending, `<ErrorMessage />` banner above form
- Links to `/signup` and `/password-reset-request` (the forgot-password route — see 2.6)
- Accessibility: `htmlFor`/`id` pairs, `aria-label` on toggle, `aria-busy` on submit
- `mutationFn` param typed as `UserLogin` (not an inline anonymous object) — the native request-body type from `types/users.ts`

```tsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { login, getCurrentUser } from "./api";
import { useAuthStore } from "./authStore";
import ErrorMessage from "../../components/ErrorMessage";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const mutation = useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      // 1) authenticate -> tokens
      const { data } = await login({ email, password });
      // 2) store tokens (persist middleware writes localStorage automatically)
      useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
      // 3) fetch full profile and cache it in the store
      const me = await getCurrentUser();
      useAuthStore.getState().setUser(me.data);
    },
    onSuccess: () => navigate("/", { replace: true }),
    // On error: mutation.error is rendered by <ErrorMessage /> below
  });

  return (
    <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-2xl font-semibold text-gray-900">Log in to Bookly</h1>

        {mutation.isError && (
          <div className="mb-4">
            <ErrorMessage error={mutation.error} />
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate({ email: email.trim(), password });
          }}
          className="space-y-4"
        >
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="relative mt-1">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••"
                className="w-full rounded-md border border-gray-300 px-3 py-2 pr-16 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute inset-y-0 right-2 text-xs font-medium text-purple-600 hover:text-purple-800"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            aria-busy={mutation.isPending}
            className="w-full rounded-md bg-purple-600 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {mutation.isPending ? "Signing in…" : "Log in"}
          </button>
        </form>

        <div className="mt-4 flex justify-between text-sm">
          <Link to="/password-reset-request" className="text-purple-600 hover:underline">
            Forgot password?
          </Link>
          <span className="text-gray-600">
            No account?{" "}
            <Link to="/signup" className="text-purple-600 hover:underline">
              Sign up
            </Link>
          </span>
        </div>
      </div>
    </div>
  );
}
```

#### 2.3.3 Register the route (`src/router.tsx`)

Incremental — only `/login` for now; remaining auth routes land in 2.9:

```tsx
children: [
  { path: "login", element: <LoginPage /> },
],
```

Public route — stays outside any future `<ProtectedRoute />` wrapper.

#### 2.3.4 Backend behavior notes

- Bad credentials → `400` `{ message: "Invalid Email Or Password", error_code: "invalid_email_or_password" }` (`InvalidCredentials` handler in `src/errors.py`)
- Rate limit exceeded → SlowAPI returns `429` with a NON-standard body (no `{message, error_code}` shape) → `parseApiError` falls back to `"An unexpected error occurred"`. Acceptable.
- Backend down / network error → same fallback path.

#### 2.3.5 Verification

1. `cd bookly-frontend && npx tsc --noEmit && npm run lint` — clean
2. Smoke test (backend `fastapi dev src/` on :8000, frontend `npm run dev` on :5173):
   - `/login` renders a centered card — no leftover template-CSS artifacts (no fixed-width bordered column)
   - Wrong creds → red alert box: "Invalid Email Or Password"
   - Correct creds → redirects to `/`; DevTools → Local Storage shows `bookly-auth` with access + refresh tokens and user
   - Browser refresh → still logged in (Zustand `persist`)
   - Submit twice fast → button disabled, label "Signing in…" while in flight

### 2.4 Build `<SignupPage />` — DETAILED SPEC (approved, ready to implement)

**Files touched:**

| File | Action |
|---|---|
| `src/features/auth/SignupPage.tsx` | Create |
| `src/router.tsx` | Modify — register public `/signup` route |

Note: LoginPage's "Forgot password?" link now points to `/password-reset-request` (the §2.6 route) — see §2.3.2.

#### 2.4.1 Backend contract (verified against `src/auth/schemas.py`)

Request body (`UserCreate`) — all fields required:

| Field | Constraint |
|---|---|
| `first_name` | ≤25 chars |
| `last_name` | ≤25 chars |
| `username` | ≤8 chars |
| `email` | valid email format, ≤40 chars |
| `password` | ≥6 chars (`PasswordStr = Annotated[str, Field(min_length=6)]`) |

(Correction vs this section's earlier draft: `first_name`/`last_name` are also capped at 25.)

Response `201`: `{ message, user: UserOut }`

Errors:
- `403 { message: "User with email already exists", error_code: "user_exists" }`
- Rate limited: **5/hour per IP** (SlowAPI) → `429` with non-standard body → `parseApiError` falls back to generic message
- FastAPI `422` validation failures also use a non-standard `{ detail: [...] }` shape — the client-side enforcement below ensures we never hit it from the UI

#### 2.4.2 Form & validation strategy

7 fields — six data fields plus client-only `confirm_password` (never sent to backend). HTML5 attributes mirror the backend schema exactly, so violations are blocked in-browser and opaque `422`s can't occur:

| Field | HTML5 attributes |
|---|---|
| first_name / last_name | `required`, `maxLength={25}`, `autoComplete="given-name"` / `"family-name"` |
| username | `required`, `maxLength={8}`, `autoComplete="username"` |
| email | `required`, `type="email"`, `maxLength={40}`, `autoComplete="email"` |
| password | `required`, `minLength={6}`, show/hide toggle (`Eye`/`EyeOff` from lucide-react, as on LoginPage) |
| confirm_password | `required`; only custom rule: `password === confirm_password` → inline red text under field + `aria-invalid`, submit blocked |

No form/validator library needed.

#### 2.4.3 Flow

```ts
const mutation = useMutation({ mutationFn: (data: UserCreate) => signup(data) });
```

- **pending** → submit disabled, label "Creating account…"
- **error** → `<ErrorMessage error={mutation.error} />` banner above form
- **success** → swap form for **success panel** (DECIDED: auto-redirect + manual CTA):
  - `CheckCircle2` icon (lucide-react), "Account created!" heading
  - Backend `message` + "check your inbox (and spam)" note
  - Visible 4-second countdown, then `navigate("/login", { replace: true })`
  - "Go to Login" CTA works immediately
  - Timer: `useEffect` + `setTimeout`, cleared on unmount
- Signup does **not** authenticate the user: no `setTokens`/`setUser` calls, nothing written to `localStorage` (verification + login still required)

#### 2.4.4 Full implementation (`src/features/auth/SignupPage.tsx`)

```tsx
import { useEffect, useState, type ChangeEvent, type SyntheticEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, Eye, EyeOff } from "lucide-react";
import { signup } from "./api";
import ErrorMessage from "../../components/ErrorMessage";
import type { UserCreate } from "../../types/users";

const initialForm: UserCreate & { confirm_password: string } = {
  first_name: "",
  last_name: "",
  username: "",
  email: "",
  password: "",
  confirm_password: "",
};

export default function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [showPassword, setShowPassword] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(4);

  const mutation = useMutation({ mutationFn: (data: UserCreate) => signup(data) });

  // Success panel: visible countdown -> auto-redirect (timer cleared on unmount)
  useEffect(() => {
    if (!mutation.isSuccess) return;
    const interval = setInterval(() => setSecondsLeft((s) => s - 1), 1000);
    const timeout = setTimeout(() => navigate("/login", { replace: true }), 4000);
    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [mutation.isSuccess, navigate]);

  const update =
    (field: keyof typeof initialForm) =>
    (e: ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));

  const onSubmit = (e: SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      setConfirmError("Passwords do not match");
      return;
    }
    setConfirmError(null);
    // Explicit field map -> exact UserCreate shape; confirm_password never sent
    const data: UserCreate = {
      first_name: form.first_name,
      last_name: form.last_name,
      username: form.username,
      email: form.email,
      password: form.password,
    };
    mutation.mutate(data);
  };

  // --- Success panel ---
  if (mutation.isSuccess) {
    return (
      <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
        <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
          <CheckCircle2 size={48} className="mx-auto text-green-600" />
          <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
            Account created!
          </h1>
          <p className="text-sm text-gray-600">
            {mutation.data?.message} Please check your inbox (and spam folder).
          </p>
          <p className="mt-2 text-sm text-gray-500">
            Redirecting to login in {Math.max(secondsLeft, 0)}s…
          </p>
          <Link
            to="/login"
            className="mt-6 inline-block rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  // --- Signup form ---
  return (
    <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-2xl font-semibold text-gray-900">
          Create your account
        </h1>

        {mutation.isError && (
          <div className="mb-4">
            <ErrorMessage error={mutation.error} />
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                First name
              </label>
              <input
                id="first_name"
                required
                maxLength={25}
                autoComplete="given-name"
                value={form.first_name}
                onChange={update("first_name")}
                placeholder="Jane"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                Last name
              </label>
              <input
                id="last_name"
                required
                maxLength={25}
                autoComplete="family-name"
                value={form.last_name}
                onChange={update("last_name")}
                placeholder="Doe"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              required
              maxLength={8}
              autoComplete="username"
              value={form.username}
              onChange={update("username")}
              placeholder="janedoe"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              maxLength={40}
              autoComplete="email"
              value={form.email}
              onChange={update("email")}
              placeholder="you@example.com"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="relative mt-1">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                minLength={6}
                autoComplete="new-password"
                value={form.password}
                onChange={update("password")}
                placeholder="At least 6 characters"
                className="w-full rounded-md border border-gray-300 px-3 py-2 pr-16 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute inset-y-0 right-2 text-xs font-medium text-purple-600 hover:text-purple-800"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <input
              id="confirm_password"
              type={showPassword ? "text" : "password"}
              required
              minLength={6}
              autoComplete="new-password"
              value={form.confirm_password}
              aria-invalid={!!confirmError}
              onChange={(e) => {
                update("confirm_password")(e);
                setConfirmError(null); // clear error as soon as user retypes
              }}
              placeholder="Repeat password"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
            {confirmError && (
              <p className="mt-1 text-xs text-red-600">{confirmError}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            aria-busy={mutation.isPending}
            className="w-full rounded-md bg-purple-600 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {mutation.isPending ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-purple-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
```

Router addition (`src/router.tsx`):

```tsx
{ path: "signup", element: <SignupPage /> },
```

#### 2.4.5 Styling & conventions

Mirror `LoginPage.tsx` exactly — same card layout utilities, input styling, Eye/EyeOff toggle pattern, disabled-button treatment. No styling-system changes in this step (UI-primitive extraction stays parked; refactor both pages uniformly later if that path is chosen).

Footer link: "Already have an account? Log in" → `/login`.

Accessibility: `htmlFor`/`id` pairs, `aria-invalid` on mismatched confirm field, `aria-busy` on submit button.

#### 2.4.6 Verification

1. `cd bookly-frontend && npx tsc --noEmit && npm run lint` — clean
2. Smoke test:
   - Typing >8 chars into username impossible (`maxLength` blocks input)
   - Password mismatch → inline red text under confirm field, **zero network requests** fired
   - Existing email → red banner: "User with email already exists"
   - Valid submit → success panel with visible countdown → auto-redirects to `/login`
   - DevTools → Local Storage shows **no** `bookly-auth` entry after signup
   - 6th signup attempt within an hour → generic rate-limit banner

### 2.5 Build `<VerifyEmailPage />` — DETAILED SPEC

**File:** `src/features/auth/VerifyEmailPage.tsx`

**Files touched:**

| File | Action |
|---|---|
| `src/features/auth/VerifyEmailPage.tsx` | Create |
| `src/router.tsx` | Modify — register `/verify/:token` route |

#### 2.5.1 Backend contract (from `src/auth/routes.py:86-107`)

`GET /auth/verify/{token}` — no auth required, token is a URL-safe JWT containing `{ email }`.

| Response | Status | Shape |
|---|---|---|
| Success | 200 | `{ message: "Account verified successfully" }` |
| Token invalid / expired / user not found | 500 | `{ message: "Error occurred during verification" }` |

The backend decodes the token, looks up the user by email, sets `is_verified: True`. If the token is expired or the user doesn't exist, it returns a generic 500 — intentionally vague to avoid leaking whether the email exists.

**Note:** Backend link format is `http://localhost:8000/api/v1/auth/verify/{token}` (raw JSON response). For Phase 2, this page will be triggered manually or by copying the token. Later (Phase 5) can repoint backend links to `http://localhost:5173/verify/{token}`.

#### 2.5.2 Design decisions

- **`useQuery` over `useMutation`** — auto-fires on mount, no user action needed. `enabled: !!token` prevents firing if URL somehow has no token.
- **No auto-redirect after success** — user should explicitly click "Log in" to see the confirmation and decide when to proceed.
- **`retry: false`** — a bad/expired token will always fail; retrying wastes a round trip and delays the error state.
- **Three UI states**: loading spinner → success card or error card. No conditional branching beyond these.
- **No resend mechanism** — backend has no dedicated resend endpoint. Verification link is generated only at signup and expires in 5 minutes. We assume the user verifies within that window.

#### 2.5.3 Full implementation (`src/features/auth/VerifyEmailPage.tsx`)

```tsx
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { verifyEmail } from "./api";
import ErrorMessage from "../../components/ErrorMessage";

export default function VerifyEmailPage() {
  const { token } = useParams<{ token: string }>();

  // useQuery auto-fires on mount — no user action needed.
  // enabled: !!token guards against /verify without a token param.
  // retry: false — a bad/expired token will always fail, no point retrying.
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["verifyEmail", token],
    queryFn: async () => {
      const { data } = await verifyEmail(token!);
      return data; // { message: "Account verified successfully" }
    },
    enabled: !!token,
    retry: false,
  });

  return (
    <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
        {/* --- Loading state --- */}
        {isLoading && (
          <>
            <Loader2
              size={48}
              className="mx-auto animate-spin text-purple-600"
            />
            <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
              Verifying your email…
            </h1>
            <p className="text-sm text-gray-600">
              This only takes a moment.
            </p>
          </>
        )}

        {/* --- Success state --- */}
        {!isLoading && !isError && data && (
          <>
            <CheckCircle2 size={48} className="mx-auto text-green-600" />
            <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
              Email verified!
            </h1>
            <p className="text-sm text-gray-600">{data.message}</p>
            <Link
              to="/login"
              className="mt-6 inline-block rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
            >
              Log in
            </Link>
          </>
        )}

        {/* --- Error state --- */}
        {!isLoading && isError && (
          <>
            <XCircle size={48} className="mx-auto text-red-600" />
            <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
              Verification failed
            </h1>
            <div className="mb-4">
              <ErrorMessage error={error} />
            </div>
            <p className="text-sm text-gray-500">
              The link may be expired or already used.
            </p>
            <Link
              to="/login"
              className="mt-4 inline-block rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
            >
              Go to Login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
```

#### 2.5.4 Router update (`src/router.tsx`)

Add inside the children array (public route, no ProtectedRoute wrapper):

```tsx
import VerifyEmailPage from "./features/auth/VerifyEmailPage";

{ path: "verify/:token", element: <VerifyEmailPage /> },
```

#### 2.5.5 Verification

1. `cd bookly-frontend && npx tsc --noEmit` — clean
2. Smoke test (backend `fastapi dev src/` on :8000, frontend `npm run dev` on :5173):
   - Navigate to `/verify/some-invalid-token` → error card: "Verification failed" + backend message + "Go to Login" link
   - Navigate to `/verify/` (no token) → page renders but query doesn't fire (`enabled: false`)
   - After signup, copy the real token from the email Celery log and navigate to `/verify/{real-token}` → success card: "Email verified!" + "Log in" link
   - Loading spinner visible during the network request (brief, ~200ms)

### 2.6 Build `<PasswordResetRequestPage />` — DETAILED SPEC

**File:** `src/features/auth/PasswordResetRequestPage.tsx`

> The earlier planned `ForgotPasswordPage.tsx` was consolidated into `PasswordResetRequestPage.tsx` — this is the canonical forgot-password page (single email field). No duplicate file exists.

**Files touched:**

| File | Action |
|---|---|
| `src/features/auth/PasswordResetRequestPage.tsx` | Create (canonical forgot-password page) |
| `src/router.tsx` | Register `password-reset-request` route |

#### 2.6.1 Backend contract (from `src/auth/routes.py:209-248`)

`POST /auth/password-reset-request` with body `PasswordResetRequest { email }`.

| Response | Status | Shape |
|---|---|---|
| Always (matched or unmatched email) | 200 | `{ message: "If an account with that email exists, a password reset link has been sent." }` |

- The backend intentionally returns the **same 200 message regardless of whether the email exists** — prevents email enumeration. Verified even for non-existent emails.
- Rate limit: **3/hour per IP** (`@limiter.limit("3/hour")` in `routes.py:212`).
- If matched, a Celery task emails a reset link. The link expires in 5 minutes (via `URLSafeTimedSerializer` `max_age=300`).

#### 2.6.2 Design decisions

- **`useMutation`** — fires on submit only, no auth needed.
- **`mutationFn` is `async` and returns `data`** via `const { data } = await requestPasswordReset(...)`. This unwraps the Axios envelope so the component reads clean `mutation.data?.message` (not `mutation.data?.data.message`). Appropriate here because the component *does* read the response message on success — matches the standard we apply consistently to the auth `useMutation` pages.
- **Success panel via early return** — when `mutation.isSuccess`, swap the form for a "Link sent!" panel with a "Back to login" link.
- **Security-aware UX** — because the backend always returns 200, the panel shows regardless of email existence; the "check your inbox (and spam)" nudge is honest and consistent.

#### 2.6.3 Full implementation (`src/features/auth/PasswordResetRequestPage.tsx`)

```tsx
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import type { PasswordResetRequest } from "../../types/users";
import { requestPasswordReset } from "./api";
import ErrorMessage from "../../components/ErrorMessage";
import { CheckCircle2 } from "lucide-react";

export default function PasswordResetRequestPage() {
  const [email, setEmail] = useState("");

  // define the mutation
  const mutation = useMutation({
    mutationFn: async ({ email }: PasswordResetRequest) => {
      const { data } = await requestPasswordReset({ email });
      return data;
    },
  });

  // --- After email send ---
  if (mutation.isSuccess) {
    return (
      <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
        <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
          <CheckCircle2 size={48} className="mx-auto text-green-600" />
          <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
            Link sent!
          </h1>
          <p className="text-sm text-gray-600">
            {mutation.data?.message}
            <br />
            Please check your inbox (and spam folder).
          </p>
          <Link
            to="/login"
            className="mt-6 inline-block rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        {mutation.isError && (
          <div className="mb-4">
            <ErrorMessage error={mutation.error} />
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate({ email: email.trim() });
          }}
          className="space-y-4"
        >
          <div className="grid gap-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
            <button
              type="submit"
              disabled={mutation.isPending}
              aria-busy={mutation.isPending}
              className="w-full rounded-md bg-purple-600 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {mutation.isPending ? "Sending..." : "Sent Password Reset Link"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

#### 2.6.4 Router registration (`src/router.tsx`)

Public route (no ProtectedRoute wrapper):

```tsx
import PasswordResetRequestPage from "./features/auth/PasswordResetRequestPage";

{ path: "password-reset-request", element: <PasswordResetRequestPage /> },
```

#### 2.6.5 Verification

1. `cd bookly-frontend && npx tsc --noEmit` — clean
2. Smoke test (backend `fastapi dev src/` on :8000, frontend `npm run dev` on :5173):
   - Navigate to `/password-reset-request` → single-email form renders, centered card
   - Submit an existing email → "Link sent!" panel with success message + "Back to login"
   - Submit a non-existent email → **same** "Link sent!" panel (backend returns 200 either way — no enumeration leak)
   - Submit twice fast → button disabled, label "Sending..." while in flight

### 2.7 Build `<ResetAccountPassword />` — DETAILED SPEC

**File:** `src/features/auth/ResetAccountPassword.tsx`

**Files touched:**

| File | Action |
|---|---|
| `src/features/auth/ResetAccountPassword.tsx` | Create |
| `src/router.tsx` | Register `password-reset-confirm/:token` route |

#### 2.7.1 Backend contract (from `src/auth/routes.py:251-288`, `src/auth/schemas.py:88-94`)

`POST /auth/password-reset-confirm/{token}` with body `PasswordResetConfirm`.

| Field | Type / constraint |
|---|---|
| `new_password` | `PasswordStr` — string, `min_length=6` |
| `confirm_new_password` | `PasswordStr` — string, `min_length=6` |

- The **backend schema enforces a match** via a model validator (`schemas.py:94`) returning 422 on mismatch.
- Success → `200 { message: "Password reset successfully" }`.
- Errors: invalid/expired token → 400 `{ detail: ... }` (raw `HTTPException` from `decode_url_safe_token`); user not found → 404; generic → 500.

#### 2.7.2 Design decisions

- **`const { token } = useParams<{ token: string }>()`** — reads the token from the URL, same rationale as VerifyEmailPage (§2.5). No `enabled: !!token` guard needed here because this is a `useMutation` (fires only on submit, not on mount).
- **`mutationFn` is `async` and returns `data`** — clean `mutation.data?.message` on success (single unwrap), matching the auth `useMutation` convention.
- **Client-side password-match check** — redundant with the backend 422 validator, but gives immediate inline feedback and avoids a wasted round-trip. Keep it (consistent with SignupPage).
- **`minLength={6}` + `required`** mirror the `PasswordStr` backend constraint so opaque 422s can't occur from the UI.
- **`autoComplete="new-password"`** on both fields — the correct HTML autocomplete token (hyphenated) so password managers autofill correctly.
- **Success panel via early return** — "Complete!" + `mutation.data?.message` + "Back to login" link.
- **Show/hide password toggle** on the new-password field only (same `Eye`/`EyeOff` pattern as LoginPage/SignupPage).

#### 2.7.3 Full implementation (`src/features/auth/ResetAccountPassword.tsx`)

```tsx
import { useMutation } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { resetPassword } from "./api";
import { CheckCircle2, Eye, EyeOff } from "lucide-react";
import ErrorMessage from "../../components/ErrorMessage";
import { useState, type ChangeEvent } from "react";
import type { PasswordResetConfirm } from "../../types/users";

const initialForm: PasswordResetConfirm = {
  new_password: "",
  confirm_new_password: "",
};

export default function ResetAccountPassword() {
  const { token } = useParams<{ token: string }>();
  const [form, setForm] = useState(initialForm);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordMisMatchError, setPasswordMisMatchError] = useState<
    string | null
  >(null);

  // define the mutation
  const mutation = useMutation({
    mutationFn: async (passwordResetConfirm: PasswordResetConfirm) => {
      const { data } = await resetPassword(token!, passwordResetConfirm);
      return data;
    },
  });

  function update(field: keyof typeof initialForm) {
    return function (e: ChangeEvent<HTMLInputElement>) {
      setForm((f) => ({ ...f, [field]: e.target.value }));
    };
  }

  // --- Success panel ---
  if (mutation.isSuccess) {
    return (
      <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
        <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
          <CheckCircle2 size={48} className="mx-auto text-green-600" />
          <h1 className="mb-2 mt-4 text-2xl font-semibold text-gray-900">
            Complete!
          </h1>
          <p className="text-sm text-gray-600">
            {mutation.data?.message}
          </p>
          <Link
            to="/login"
            className="mt-6 inline-block rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-svh items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-2xl font-semibold text-gray-900">
          Enter new password
        </h1>

        {mutation.isError && (
          <div className="mb-4">
            <ErrorMessage error={mutation.error} />
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();

            if (form.new_password != form.confirm_new_password) {
              setPasswordMisMatchError("Passwords did not match");
              return;
            }

            setPasswordMisMatchError(null);

            const data: PasswordResetConfirm = {
              new_password: form.new_password,
              confirm_new_password: form.confirm_new_password,
            };

            mutation.mutate(data);
          }}
          className="space-y-4"
        >
          <div className="grid gap-4">
            <div>
              <label
                htmlFor="new_password"
                className="block text-sm font-medium text-gray-700"
              >
                New Password
              </label>
              <div className="relative mt-1">
                <input
                  id="new_password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={6}
                  autoComplete="new-password"
                  value={form.new_password}
                  onChange={update("new_password")}
                  placeholder="At least 6 characters"
                  className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute inset-y-0 right-2 text-xs font-medium text-purple-600 hover:text-purple-800"
                >
                  {form.new_password && (
                    <span>
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </span>
                  )}
                </button>
              </div>
            </div>

            <div>
              <label
                htmlFor="confirm_new_password"
                className="block text-sm font-medium text-gray-700"
              >
                Confirm New Password
              </label>
              <input
                id="confirm_new_password"
                type={showPassword ? "text" : "password"}
                required
                minLength={6}
                autoComplete="new-password"
                value={form.confirm_new_password}
                aria-invalid={!!passwordMisMatchError}
                onChange={(e) => {
                  update("confirm_new_password")(e);
                  setPasswordMisMatchError(null); // clear error as soon as user retypes
                }}
                placeholder="Repeat password"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
              {passwordMisMatchError && (
                <p className="mt-1 text-xs text-red-600">
                  {passwordMisMatchError}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={mutation.isPending}
              aria-busy={mutation.isPending}
              className="w-full rounded-md bg-purple-600 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Change password
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

#### 2.7.4 Router registration (`src/router.tsx`)

Public route — uses the **absolute path matching the backend email link format** so clicks from the emailed link land directly:

```tsx
import ResetAccountPassword from "./features/auth/ResetAccountPassword";

{
  path: "/api/v1/auth/password-reset-confirm/:token",
  element: <ResetAccountPassword />,
},
```

#### 2.7.5 Verification

1. `cd bookly-frontend && npx tsc --noEmit` — clean
2. Smoke test:
   - Password mismatch → inline red "Passwords did not match" under the confirm field, **zero network requests** fired
   - Valid submit (real token copied from email Celery log, navigate to `/api/v1/auth/password-reset-confirm/{token}`) → "Complete!" panel + "Back to login"
   - Navigate with a bogus token → error banner (400/404/500 from backend)

### 2.8 Build shared components — DETAILED SPEC

Four shared components live in `src/components/`. All four now exist on disk (synced from the codebase). `<Layout />` is **wired into `App.tsx`** (App renders `<Layout />`, so the NavBar + `main` + `<Outlet />` shell wraps every route). `<ProtectedRoute />` is created but **not yet mounted** — it gets added to the router in Phase 3 (§3.6). Until then the auth routes remain public children of `<App />`. A **fifth** shared component, `<ConfirmDialog />`, is added in Phase 3 §3.5 (reused there for book-delete and later in Phase 4 for review/tag confirmation).

**Files touched:**

| File | Action |
|---|---|
| `src/components/ErrorMessage.tsx` | Already built (step 2.3) — do not duplicate |
| `src/components/Loading.tsx` | Built — synced from disk |
| `src/components/NavBar.tsx` | Built — synced from disk |
| `src/components/ProtectedRoute.tsx` | Built — synced from disk |
| `src/components/Layout.tsx` | Built — synced from disk |
| `src/App.tsx` | Wiring — renders `<Layout />` (was `<Outlet />`) |
| `src/components/ConfirmDialog.tsx` | Phase 3 — reused for delete confirmation (§3.5) |

#### 2.8.1 `<ErrorMessage />` — already exists, reference only

Built in step 2.3 (pulled forward because LoginPage depends on it). Do **not** rebuild.

- Props: `{ error: unknown }`
- Uses `parseApiError(error)` from `src/lib/errors.ts` to extract `{ message, resolution? }`
- Renders a `role="alert"` red-bordered div with the message (and resolution line if present). Live file confirmed at `src/components/ErrorMessage.tsx`.

#### 2.8.2 `<Loading />` — spinner

**File:** `src/components/Loading.tsx` (synced from disk)

Design decisions:
- A lightweight spinner (lucide `Loader2` with an `animate-spin` class) rather than a heavy skeleton grid.
- Optional `fullPage?: boolean` (default `false`) and `size?: number` (default `48`).
- When `fullPage` is truthy: renders a **fixed full-screen overlay** (`fixed inset-0 z-50`) centered over the page, and bumps the spinner size by `+16` (`size + 16`) so it reads larger in the empty viewport.
- When `fullPage` is false/omitted: renders inline (`flex justify-center p-8`) at the given `size` (default `48`), for use inside already-padded containers.

Exact disk implementation:

```tsx
import { Loader2 } from "lucide-react";
export default function Loading({
  fullPage = false,
  size = 48,
}: {
  fullPage?: boolean;
  size?: number;
}) {
  return (
    <div
      className={
        fullPage
          ? "fixed inset-0 z-50 flex items-center justify-center bg-gray-100"
          : "flex justify-center p-8"
      }
      role="status"
      aria-label="Loading"
    >
      <Loader2
        size={fullPage ? size + 16 : size}
        className="animate-spin text-purple-600"
      />
    </div>
  );
}
```

Usage (Phase 3/4): `<Loading />` for inline states; `<Loading fullPage />` for page-level loading (see the Phase 5 §5.1 load/empty-state table).

#### 2.8.3 `<NavBar />` — top nav, conditional on auth

**File:** `src/components/NavBar.tsx` (synced from disk)

Design decisions:
- Read auth via `useAuth()` (`src/features/auth/useAuth.ts`) — reactive subscription to the Zustand store (`user`, `isAuthenticated`).
- **Not authenticated:** "Login" + "Signup" links (clean relative paths, matching router).
- **Authenticated:** show the user's full name (`user.first_name` + `user.last_name`), a "Books" link (points to `/books`; wired meaningfully in §3.7), and a "Logout" button.
- **Logout handler** must: call the `logout()` API to hit `GET /auth/logout` (which adds the JTI to the Redis blocklist), then clear the Zustand store (`useAuthStore.getState().logout()`), then navigate to `/login`. Use `useNavigate` from react-router-dom.
- Styling: `bg-purple-700` bar with white text, `flex justify-between items-center` — matches the purple accent used across auth pages.

```tsx
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";
import { useAuthStore } from "../features/auth/authStore";
import { logout } from "../features/auth/api";

export default function NavBar() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      useAuthStore.getState().logout();
      navigate("/login");
    }
  };

  return (
    <nav className="flex items-center justify-between bg-purple-700 px-6 py-3 text-white">
      <div className="text-lg font-semibold">
        <Link to="/">Bookly</Link>
      </div>

      {isAuthenticated() ? (
        <div className="flex items-center gap-4 text-sm">
          <Link to="/books" className="hover:underline">
            Books
          </Link>
          <span>{user?.first_name} {user?.last_name}</span>
          <button
            onClick={handleLogout}
            className="rounded bg-purple-900 px-3 py-1 text-xs font-semibold hover:bg-purple-800"
          >
            Logout
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-4 text-sm">
          <Link to="/login" className="hover:underline">
            Login
          </Link>
          <Link to="/signup" className="hover:underline">
            Signup
          </Link>
        </div>
      )}
    </nav>
  );
}
```

#### 2.8.4 `<ProtectedRoute />` — redirect if not authenticated

**File:** `src/components/ProtectedRoute.tsx` (synced from disk)

- Reads `isAuthenticated` from `useAuth()`.
- If not authenticated, `<Navigate to="/login" replace />`; else renders `<Outlet />` so nested/child routes render inside the guard.
- Same implementation as the original §2.8 sketch (no dependency on the now-deprecated plan paths).

```tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  //   Either /login or Outlet
  if (!isAuthenticated()) return <Navigate to="/login" replace />;
  return <Outlet />;
}
```

#### 2.8.5 `<Layout />` — NavBar + routed content

**File:** `src/components/Layout.tsx` (synced from disk)

- Renders `<NavBar />` at top and `<main><Outlet /></main>` below.
- In Phase 3, protected pages sit under `<ProtectedRoute />` inside a `<Layout />` route (see §2.9 note + §3.6).
- The disk file also carries a trailing JSX-comment block explaining `<main>`/`<Outlet />` semantics — harmless, leave it in place.

```tsx
import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";

export default function Layout() {
  return (
    <div className="min-h-svh bg-gray-100">
      <NavBar />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
```

#### 2.8.6 Wiring — `Layout` mounted via `App.tsx`

`App.tsx` now renders `<Layout />` (instead of the bare `<Outlet />`), so the `NavBar` + `main` + `<Outlet />` shell wraps **every** route in Phase 2:

```tsx
// src/App.tsx
import Layout from "./components/Layout";

export default function App() {
  return <Layout />;
}
```

Consequences:
- `NavBar` renders on all routes and switches between Login/Signup (logged out) and full-name + Books + Logout (logged in).
- `<Layout />` is **not** referenced in `router.tsx` — the router still lists each auth route as a public child of `<App />` (§2.9 matches disk).
- `<ProtectedRoute />` is created but **not yet mounted**. Only Phase 3 §3.6 nests the protected books pages under `ProtectedRoute` (inside `Layout`), and §3.7 finalizes the `NavBar` "Books" link target.

#### 2.8.7 Verification

1. `cd bookly-frontend && npx tsc --noEmit` — clean.
2. `npm run lint` — clean.
3. Visual smoke test (backend `fastapi dev src/` on :8000, frontend `npm run dev` on :5173): now that `Layout`/`NavBar` render on every route —
   - Logged out: purple NavBar shows "Bookly" + Login + Signup links on `/login`, `/signup`, `/password-reset-request`.
   - Logged in: NavBar shows the user's full name + Books + Logout; clicking Logout returns to `/login` and clears `bookly-auth`.


### 2.9 Update `router.tsx` with auth routes

Live snapshot (matches `src/router.tsx` at end of Phase 2). All routes are public children of `<App />`; `App` renders `<Layout />` (see §2.8.6). Only `<ProtectedRoute />` wrapping of the books pages is deferred to Phase 3.

```tsx
import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import LoginPage from "./features/auth/LoginPage";
import SignupPage from "./features/auth/SignupPage";
import VerifyEmailPage from "./features/auth/VerifyEmailPage";
import PasswordResetRequestPage from "./features/auth/PasswordResetRequestPage";
import ResetAccountPassword from "./features/auth/ResetAccountPassword";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      // Routes added in Phase 2
      { path: "login", element: <LoginPage /> },
      { path: "signup", element: <SignupPage /> },
      { path: "/api/v1/auth/verify/:token", element: <VerifyEmailPage /> },
      { path: "password-reset-request", element: <PasswordResetRequestPage /> },
      {
        path: "/api/v1/auth/password-reset-confirm/:token",
        element: <ResetAccountPassword />,
      },
    ],
  },
]);
```

Route-path rationale (DECIDED — keep current, not the cleaner `/forgot-password`/`/reset-password/:token` plan):
- `verify/:token` and `password-reset-confirm/:token` use the **absolute `…/api/v1/…` paths** so links generated in backend emails land directly on the correct page (no client-side redirect needed).
- `password-reset-request` is a frontend-only navigation path (reached via the "Forgot password?" link), so it uses the clean relative path.

Phase 3 (Books) will mount `<ProtectedRoute />` around the books pages (inside the `Layout` shell already wired in §2.8.6) and add them to this router.

### 2.10 Manual smoke test for auth flow

1. Run backend: `fastapi dev src/` (port 8000)
2. Run frontend: `npm run dev` (port 5173)
3. Sign up → success panel ("check your inbox") appears, auto-redirects to `/login` after ~4s; confirm NO `bookly-auth` localStorage entry yet (see 2.4.6)
4. Manually call verify endpoint (backend sends email via Celery, or hit the link directly)
5. Login → confirm `localStorage` has `bookly-auth` key with tokens + user
6. Refresh page → confirm tokens persist (Zustand `persist` middleware)
7. Navigate to `/` → confirm `<ProtectedRoute>` shows (or redirects to login if logged out)
8. `/password-reset-request` → submit email → "Link sent!" panel regardless of email existence (see 2.6)
9. Paste a reset link (from Celery log) into the browser → `/api/v1/auth/password-reset-confirm/{token}` → reset form (see 2.7)

---

## Phase 3 — Books CRUD
Books CRUD: typed API client, TanStack Query hooks with cache invalidation, BooksList, BookDetail, BookForm (shared create/edit)


### 3.1 Build books API helper (`src/features/books/api.ts`) — DETAILED SPEC

**File:** `src/features/books/api.ts`

**Files touched:**

| File | Action |
|---|---|
| `src/features/books/api.ts` | Create |
| `src/types/books.ts` | Already built (Phase 1) — `BookBase/BookCreate/BookUpdate/BookOut/BookDetailOut` |

Backend contract (verified against `src/books/routes.py`):

| Function | HTTP call | Auth | Success → returns |
|---|---|---|---|
| `getBooks()` | `GET /books/` | Yes | **200** → `BookOut[]` (newest first, nested `tags`) |
| `getBook(uid)` | `GET /books/{uid}` | Yes | **200** → `BookDetailOut` (nested `reviews` + `tags`) |
| `createBook(data)` | `POST /books/` | Yes | **201** → `BookOut` |
| `updateBook(uid, data)` | `PATCH /books/{uid}` | Yes | **200** → `BookOut` |
| `deleteBook(uid)` | `DELETE /books/{uid}` | Yes | **204** (empty body) |

- Auth: any **verified** user (`RoleChecker(["admin","user"])`). No per-user ownership check on update/delete in this version.
- `getBook` returns a `BookDetailOut` — nested `reviews` are rendered on the detail page (no standalone reviews list page for users).
- `deleteBook` returns **204 with no body** — the mutation should not expect `data`.

```ts
import apiClient from "../../lib/apiClient";
import type {
  BookOut,
  BookDetailOut,
  BookCreate,
  BookUpdate,
} from "../../types/books";

const PREFIX = "books";

export const getBooks = () => apiClient.get<BookOut[]>(`/${PREFIX}/`);

export const getBook = (uid: string) =>
  apiClient.get<BookDetailOut>(`/${PREFIX}/${uid}`);

export const createBook = (data: BookCreate) =>
  apiClient.post<BookOut>(`/${PREFIX}/`, data);

export const updateBook = (uid: string, data: BookUpdate) =>
  apiClient.patch<BookOut>(`/${PREFIX}/${uid}`, data);

export const deleteBook = (uid: string) =>
  apiClient.delete(`/${PREFIX}/${uid}`); // returns 204, no body
```
- Same `PREFIX` convention as §2.1 (`const PREFIX = "books"`, no slashes; call sites add them). Note `getBooks`/`createBook` use `` `/${PREFIX}/` `` → `/books/` (trailing slash — the backend's list/create routes), while detail/update/delete use `` `/${PREFIX}/${uid}` `` → `/books/{uid}`. The list return type is `BookOut[]` (a real array, not a tuple).

**Error shapes from `errors.py`:**
- `BookNotFound`: 404 `{ message: "Book not found", error_code: "book_not_found" }`
- `NotAuthenticated` / `InvalidToken`: 401 (no / bad token)
- `AccountNotVerified`: 403 `{ message: "Account Not verified", error_code: "account_not_verified" }`
- SlowAPI 429 returns non-standard `{ "detail": ... }` (falls through `parseApiError` to a generic message)

### 3.2 Create books queries/mutations (`src/features/books/queries.ts`) — DETAILED SPEC

**File:** `src/features/books/queries.ts`

Design decisions:
- `bookKeys` centralizes query-key identity so all hooks (and any manual invalidation) stay in sync.
- `useBooks` reads the list; `useBook(uid)` guards with `enabled: !!uid` (same pattern as `useCurrentUser`).
- Mutation `onSuccess` invalidations:
  - `useCreateBook` → invalidate `bookKeys.all` (list may have changed / sort order).
  - `useUpdateBook(uid)` → invalidate `bookKeys.all` **and** `bookKeys.detail(uid)`.
  - `useDeleteBook` → invalidate `bookKeys.all`.
- `mutationFn` here returns the axios promise directly (nothing reads `data` at hook level; pages unwrap where needed).

```ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBooks, getBook, createBook, updateBook, deleteBook } from "./api";
import type { BookCreate, BookUpdate } from "../../types/books";

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

### 3.3 Build `<BooksListPage />` — DETAILED SPEC

**File:** `src/features/books/BooksListPage.tsx`

Design decisions:
- `useBooks()` query; branch on `isLoading` → `<Loading />`, `isError` → `<ErrorMessage />`, empty list → empty-state CTA, else grid of cards.
- Each card is a `<Link to={/books/${book.uid}}>` showing title, author, publisher, language, and tag chips (`book.tags.map`). Phase 4 replaces the inline chips with the shared `<TagChips />`.
- A prominent "Create Book" button → `/books/new`.
- Page shell: the `Layout` (NavBar) already wraps all routes via `App`, so this page only renders its content column.

```tsx
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { useBooks } from "./queries";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";

export default function BooksListPage() {
  const { data: books, isLoading, isError, error } = useBooks();

  if (isLoading) return <Loading />;
  if (isError) return <ErrorMessage error={error} />;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Books</h1>
        <Link
          to="/books/new"
          className="inline-flex items-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-700"
        >
          <Plus size={16} /> Create Book
        </Link>
      </div>

      {books && books.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-600">No books yet. Create your first book!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {books?.map((book) => (
            <Link
              key={book.uid}
              to={`/books/${book.uid}`}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
            >
              <h2 className="mb-1 font-semibold text-gray-900">{book.title}</h2>
              <p className="text-sm text-gray-600">by {book.author}</p>
              <p className="mt-2 text-xs text-gray-500">
                {book.publisher} · {book.language}
              </p>
              {book.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {book.tags.map((tag) => (
                    <span
                      key={tag.uid}
                      className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-700"
                    >
                      {tag.name}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 3.4 Build `<BookForm />` — DETAILED SPEC

**File:** `src/features/books/BookForm.tsx`

Design decisions:
- A **single shared component** toggled by a `mode: "create" | "edit"` prop — no separate create/edit pages.
- Props: `mode`, `bookUid?: string` (edit only), `initialData?: BookUpdate` (edit only — used to prefill the controlled state).
- Controlled fields: `title`, `author`, `publisher`, `page_count` (number), `language`, `published_date` (`<input type="date">`).
- Client validation (submission guard, matches backend `BookBase`): all required; `page_count` must be a positive integer.
- Submit: create → `useCreateBook().mutateAsync(data)` then `navigate(/books/${created.uid})`; edit → `useUpdateBook(bookUid).mutateAsync(data)` then `navigate(/books/${bookUid})`.
- React 19: use `SyntheticEvent<HTMLFormElement>` for the submit handler (not the deprecated `FormEvent`).
- Backend note: `published_date` is sent as a raw `"YYYY-MM-DD"` string; `BookUpdate` makes every field optional; `BookCreate.published_date` defaults to `"YYYY-MM-DD"`.

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type ChangeEvent, type SyntheticEvent } from "react";
import { useNavigate } from "react-router-dom";
import { createBook, updateBook } from "./api";
import { bookKeys } from "./queries";
import ErrorMessage from "../../components/ErrorMessage";
import type { BookCreate, BookUpdate } from "../../types/books";

export default function BookForm({
  mode,
  bookUid,
  initialData,
}: {
  mode: "create" | "edit";
  bookUid?: string;
  initialData?: BookUpdate;
}) {
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [form, setForm] = useState({
    title: initialData?.title ?? "",
    author: initialData?.author ?? "",
    publisher: initialData?.publisher ?? "",
    page_count: initialData?.page_count?.toString() ?? "",
    language: initialData?.language ?? "",
    published_date: initialData?.published_date ?? "",
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async () =>
      mode === "create"
        ? createBook(castCreate())
        : updateBook(bookUid!, castUpdate()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: bookKeys.all });
    },
  });

  function castCreate(): BookCreate {
    return {
      ...form,
      page_count: Number(form.page_count),
      published_date: form.published_date,
    };
  }

  function castUpdate(): BookUpdate {
    return {
      ...(form.title ? { title: form.title } : {}),
      ...(form.author ? { author: form.author } : {}),
      ...(form.publisher ? { publisher: form.publisher } : {}),
      ...(form.page_count ? { page_count: Number(form.page_count) } : {}),
      ...(form.language ? { language: form.language } : {}),
      ...(form.published_date ? { published_date: form.published_date } : {}),
    };
  }

  function update(field: keyof typeof form) {
    return (e: ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    const pageCount = Number(form.page_count);
    if (!form.title || !form.author || !form.publisher || !form.language) {
      setValidationError("All fields are required.");
      return;
    }
    if (!Number.isInteger(pageCount) || pageCount <= 0) {
      setValidationError("Page count must be a positive integer.");
      return;
    }
    setValidationError(null);

    // mutationFn closes over `form`; mutateAsync() (no args) resolves to the
    // axios response, so we can grab the created uid for the redirect.
    const res = await mutation.mutateAsync();
    const uid = mode === "create" ? res.data.uid : bookUid!;
    navigate(`/books/${uid}`);
  }

  return (
    <div className="mx-auto max-w-lg rounded-lg bg-white p-6 shadow-md">
      <h1 className="mb-4 text-xl font-semibold text-gray-900">
        {mode === "create" ? "Create Book" : "Edit Book"}
      </h1>

      {mutation.isError && (
        <div className="mb-4">
          <ErrorMessage error={mutation.error} />
        </div>
      )}
      {validationError && (
        <div className="mb-4">
          <ErrorMessage
            error={{ message: validationError, error_code: "validation" }}
          />
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {(
          [
            ["title", "Title"],
            ["author", "Author"],
            ["publisher", "Publisher"],
            ["language", "Language"],
          ] as const
        ).map(([field, label]) => (
          <div key={field}>
            <label className="block text-sm font-medium text-gray-700">
              {label}
            </label>
            <input
              value={form[field]}
              onChange={update(field)}
              required
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>
        ))}

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Page count
          </label>
          <input
            type="number"
            min={1}
            value={form.page_count}
            onChange={update("page_count")}
            required
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Published date
          </label>
          <input
            type="date"
            value={form.published_date}
            onChange={update("published_date")}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-md bg-purple-600 py-2 text-sm font-semibold text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {mutation.isPending
            ? mode === "create"
              ? "Creating..."
              : "Saving..."
            : mode === "create"
              ? "Create Book"
              : "Save Changes"}
        </button>
      </form>
    </div>
  );
}
```

### 3.5 Build `<ConfirmDialog />` + `<BookDetailPage />` — DETAILED SPEC

Phase 3 adds the **fifth shared component** `<ConfirmDialog />` (reused later in Phase 4 for review/tag deletes) and uses it on `BookDetailPage` for the delete action.

#### 3.5.1 `<ConfirmDialog />` (reusable shared component)

**File:** `src/components/ConfirmDialog.tsx`

Props:
- `open: boolean` — show/hide the modal.
- `title: string` — heading.
- `message?: string` — optional body text.
- `confirmLabel?: string` — confirm button text (default `"Confirm"`).
- `onCancel: () => void`, `onConfirm: () => void`.
- Accessible: `role="dialog" aria-modal="true"`, fixed full-screen overlay, focus on the confirm button.

```tsx
import { useEffect, useRef } from "react";

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Confirm",
  onCancel,
  onConfirm,
}: {
  open: boolean;
  title: string;
  message?: string;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const confirmRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (open) confirmRef.current?.focus();
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-full max-w-sm rounded-lg bg-white p-6 shadow-lg"
      >
        <h2 className="mb-2 text-lg font-semibold text-gray-900">{title}</h2>
        {message && <p className="mb-4 text-sm text-gray-600">{message}</p>}
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            ref={confirmRef}
            onClick={onConfirm}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### 3.5.2 `<BookDetailPage />`

**File:** `src/features/books/BookDetailPage.tsx`

Design decisions:
- `const { uid } = useParams<{ uid: string }>()` (explicit generic required — see §2.5 note); `useBook(uid)` with `enabled: !!uid`.
- States: `isLoading` → `<Loading />`; `isError` → `<ErrorMessage />` (covers 404 `book_not_found`).
- Displays all backend fields; renders placeholders for `<TagChips />`, `<ReviewList />`, `<ReviewForm />` — wired in Phase 4.
- **Edit** → `<Link to={/books/${uid}/edit}>`.
- **Delete** → open the **inline `<ConfirmDialog />`** via `showDeleteConfirm` state; on confirm → `useDeleteBook().mutateAsync(uid)` → `navigate("/books")`; on cancel → close. No `window.confirm`.

```tsx
import { Link, useNavigate, useParams } from "react-router-dom";
import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { useBook, useDeleteBook } from "./queries";
import Loading from "../../components/Loading";
import ErrorMessage from "../../components/ErrorMessage";
import ConfirmDialog from "../../components/ConfirmDialog";

export default function BookDetailPage() {
  const { uid } = useParams<{ uid: string }>();
  const navigate = useNavigate();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: book, isLoading, isError, error } = useBook(uid ?? "");

  const deleteMutation = useDeleteBook();

  async function handleDelete() {
    setShowDeleteConfirm(false);
    await deleteMutation.mutateAsync(uid!);
    navigate("/books");
  }

  if (isLoading) return <Loading />;
  if (isError || !book) return <ErrorMessage error={error} />;

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">{book.title}</h1>
        <div className="flex gap-2">
          <Link
            to={`/books/${book.uid}/edit`}
            className="inline-flex items-center gap-1 rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white hover:bg-purple-700"
          >
            <Pencil size={14} /> Edit
          </Link>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="inline-flex items-center gap-1 rounded-md border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
          >
            <Trash2 size={14} /> Delete
          </button>
        </div>
      </div>

      <div className="space-y-2 rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-700">
        <p><span className="font-medium">Author:</span> {book.author}</p>
        <p><span className="font-medium">Publisher:</span> {book.publisher}</p>
        <p><span className="font-medium">Pages:</span> {book.page_count}</p>
        <p><span className="font-medium">Language:</span> {book.language}</p>
        <p>
          <span className="font-medium">Published:</span> {book.published_date}
        </p>
      </div>

      {/* -- Phase 4: <TagChips bookUid={uid} tags={book.tags} /> -- */}
      {/* -- Phase 4: <ReviewList reviews={book.reviews} /> -- */}
      {/* -- Phase 4: <ReviewForm bookUid={uid} /> -- */}

      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete book?"
        message={`Are you sure you want to delete "${book.title}"? This cannot be undone.`}
        confirmLabel="Delete"
        onCancel={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
```

### 3.6 Restructure `router.tsx` — mount `<ProtectedRoute />` + books routes — DETAILED SPEC

`ProtectedRoute` (built in §2.8.4) is now mounted as a **pathless layout route** whose children are the books pages. Because `App` already renders `<Layout />` (NavBar + `<Outlet />`), the books pages get the NavBar automatically; `ProtectedRoute` adds the auth guard so unauthenticated visitors are redirected to `/login`.

The auth routes remain **public** children of `App` (above the protected block). Full updated snapshot (`src/router.tsx`):

```tsx
import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./features/auth/LoginPage";
import SignupPage from "./features/auth/SignupPage";
import VerifyEmailPage from "./features/auth/VerifyEmailPage";
import PasswordResetRequestPage from "./features/auth/PasswordResetRequestPage";
import ResetAccountPassword from "./features/auth/ResetAccountPassword";
import BooksListPage from "./features/books/BooksListPage";
import BookDetailPage from "./features/books/BookDetailPage";
import BookForm from "./features/books/BookForm";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      // Public auth routes
      { path: "login", element: <LoginPage /> },
      { path: "signup", element: <SignupPage /> },
      { path: "/api/v1/auth/verify/:token", element: <VerifyEmailPage /> },
      { path: "password-reset-request", element: <PasswordResetRequestPage /> },
      {
        path: "/api/v1/auth/password-reset-confirm/:token",
        element: <ResetAccountPassword />,
      },
      // Protected books routes
      {
        element: <ProtectedRoute />,
        children: [
          { path: "books", element: <BooksListPage /> },
          { path: "books/new", element: <BookForm mode="create" /> },
          { path: "books/:uid", element: <BookDetailPage /> },
          { path: "books/:uid/edit", element: <BookForm mode="edit" /> },
        ],
      },
    ],
  },
]);
```

### 3.7 NavBar "Books" link — reconciliation note

The `NavBar` already renders a "Books" link pointing to `/books` (built in §2.8.3). No code change is needed here — §3.6's `/books` route is what now serves that link. Just confirm the link exists and that `/books` resolves to `BooksListPage` for an authenticated user (and redirects to `/login` otherwise).

### 3.8 Verification — DETAILED SPEC

1. `cd bookly-frontend && npx tsc --noEmit` — clean.
2. `npm run lint` — clean.
3. Manual smoke test (backend `fastapi dev src/` on :8000, frontend `npm run dev` on :5173):
   - **Logged out:** visiting `/books` redirects to `/login` (ProtectedRoute). NavBar shows Login/Signup.
   - **Login:** NavBar shows full name + Books + Logout.
   - **List:** `/books` shows empty state "No books yet. Create your first book!". "Create Book" → `/books/new`.
   - **Create:** submit valid form → redirects to `/books/{uid}` detail; back on `/books`, the new book is listed (newest first).
   - **Edit:** on detail → Edit → `/books/{uid}/edit` prefilled → save → detail shows updated fields.
   - **Delete dialog:** open Delete → **Cancel** closes with no change; open again → **Delete** → confirm dialog closes, navigates to `/books`, book gone.
   - **Bad uid:** visit `/books/not-a-real-uid` → `<ErrorMessage />` shows "Book not found" (404).
   - **Validation:** in the form, a non-positive `page_count` or missing required field shows inline validation and does not submit.

---

## Phase 4 — Reviews + Tags
Reviews + Tags: add/delete reviews inline on BookDetail, TagChips with add/remove, full tag CRUD

### 4.1 Build reviews API helper (`src/features/reviews/api.ts`)

| Function | Backend route | Auth required | Request body | Response |
|---|---|---|---|---|
| `getReviews()` | `GET /reviews/` | Admin only | — | `ReviewOut[]` |
| `getReview(uid)` | `GET /reviews/{uid}` | User/Admin | — | `ReviewOut` |
| `addReview(bookUid, data)` | `POST /reviews/book/{book_uid}` | User/Admin | `ReviewCreate` | `ReviewOut` |
| `deleteReview(uid)` | `DELETE /reviews/{uid}` | User/Admin | — | 204 |

```ts
import apiClient from "../../lib/apiClient";
import type { ReviewOut, ReviewCreate } from "../../types/reviews";

export const getReviews = () => apiClient.get<ReviewOut[]>("/reviews/");

export const getReview = (uid: string) =>
  apiClient.get<ReviewOut>(`/reviews/${uid}`);

export const addReview = (bookUid: string, data: ReviewCreate) =>
  apiClient.post<ReviewOut>(`/reviews/book/${bookUid}`, data);

export const deleteReview = (uid: string) =>
  apiClient.delete(`/reviews/${uid}`);
```

**Error shapes:**
- `ReviewNotFound`: 404 `{ message: "Review Not Found", error_code: "review_not_found" }`
- `InsufficientPermission`: 401 `{ message: "You do not have enough permissions...", error_code: "insufficient_permissions" }`

### 4.2 Create reviews queries/mutations (`src/features/reviews/queries.ts`)

```ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addReview, deleteReview } from "./api";
import type { ReviewCreate } from "../../types/reviews";
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

**Note:** Reviews are nested inside `BookDetailOut` (the `GET /books/{uid}` response includes `reviews: ReviewOut[]`). There is no standalone reviews list page for users — reviews are displayed inline on `<BookDetailPage />`. The `GET /reviews/` (admin-only) endpoint exists but is optional for Phase 4.

### 4.3 Build `<ReviewList />`

**File:** `src/features/reviews/ReviewList.tsx`

- Accept `reviews: ReviewOut[]` prop (from `BookDetailOut.reviews`)
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
| `getTags()` | `GET /tags/` | User/Admin | — | `TagOut[]` |
| `createTag(data)` | `POST /tags/` | User/Admin | `{ name }` | `TagOut` |
| `addTagsToBook(bookUid, data)` | `POST /tags/book/{book_uid}/tags` | User/Admin | `{ tags: [{ name }] }` | `BookOut` |
| `updateTag(uid, data)` | `PUT /tags/{uid}` | User/Admin | `{ name }` | `TagOut` |
| `deleteTag(uid)` | `DELETE /tags/{uid}` | User/Admin | — | 204 |

```ts
import apiClient from "../../lib/apiClient";
import type { TagOut, TagCreate, TagAdd, BookOut } from "../../types/tags";

export const getTags = () => apiClient.get<TagOut[]>("/tags/");

export const createTag = (data: TagCreate) =>
  apiClient.post<TagOut>("/tags/", data);

export const addTagsToBook = (bookUid: string, data: TagAdd) =>
  apiClient.post<BookOut>(`/tags/book/${bookUid}/tags`, data);

export const updateTag = (uid: string, data: TagCreate) =>
  apiClient.put<TagOut>(`/tags/${uid}`, data);

export const deleteTag = (uid: string) =>
  apiClient.delete(`/tags/${uid}`);
```

**Error shapes:**
- `TagNotFound`: 404 `{ message: "Tag Not Found", error_code: "tag_not_found" }`
- `TagAlreadyExists`: 403 `{ message: "Tag Already exists", error_code: "tag_exists" }`

### 4.6 Create tags queries/mutations (`src/features/tags/queries.ts`)

```ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getTags, createTag, addTagsToBook, updateTag, deleteTag } from "./api";
import type { TagCreate, TagAdd } from "../../types/tags";
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

- Accept `bookUid: string` and `tags: TagOut[]` props
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
import type { LoginResponse } from "../../types/users";
import type { BookOut } from "../../types/books";

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
    const books: BookOut[] = [
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
