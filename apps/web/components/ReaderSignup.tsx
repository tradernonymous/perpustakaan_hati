import { LibraryLogin } from "@/components/LibraryLogin";
import { googleReaderConfig } from "@/src/server/google-reader";

export function ReaderSignup({ returnPage }: { returnPage?: number | null }) {
  const google = googleReaderConfig();
  const googleHref = returnPage ? `/api/pustaka/google?halaman=${returnPage}` : "/api/pustaka/google";

  return (
    <div className="mx-auto grid max-w-reading gap-3">
      {google && (
        <a href={googleHref} className="btn-ghost flex min-h-tap items-center justify-center gap-3">
          <svg aria-hidden="true" viewBox="0 0 48 48" width="21" height="21">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.2 3.61l6.85-6.85C35.89 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5Z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.93c-.58 2.96-2.22 5.47-4.73 7.16l7.74 6.01c4.52-4.18 7.04-10.34 7.04-17.64Z"/>
            <path fill="#FBBC05" d="M10.53 28.59a14.4 14.4 0 0 1 0-9.18l-7.98-6.19a24 24 0 0 0 0 21.56l7.98-6.19Z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.9-5.79l-7.74-6.01c-2.15 1.45-4.91 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.5 42.62 14.62 48 24 48Z"/>
          </svg>
          Teruskan dengan Google
        </a>
      )}
      {google && <p className="text-sm text-fg-muted">Dalam TikTok atau Threads, buka laman ini dalam pelayar telefon jika Google tersekat, atau gunakan e-mel di bawah.</p>}
      <LibraryLogin returnPage={returnPage} />
    </div>
  );
}
