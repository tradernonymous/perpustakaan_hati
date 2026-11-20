import { LibraryLogin } from "@/components/LibraryLogin";
import { googleReaderConfig } from "@/src/server/google-reader";

export function ReaderSignup({ returnPage }: { returnPage?: number | null }) {
  const google = googleReaderConfig();
  const googleHref = returnPage ? `/api/pustaka/google?halaman=${returnPage}` : "/api/pustaka/google";

  return (
    <div className="mx-auto grid max-w-reading gap-3">
      {google && (
        <a href={googleHref} className="ph-cta flex min-h-tap items-center justify-center">
          Teruskan dengan Google
        </a>
      )}
      {google && <p className="text-sm text-fg-muted">Dalam TikTok atau Threads, buka laman ini dalam pelayar telefon jika Google tersekat, atau gunakan e-mel di bawah.</p>}
      <LibraryLogin returnPage={returnPage} />
    </div>
  );
}
