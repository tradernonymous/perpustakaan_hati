/**
 * Design System 3.3 lowercase author byline with rainbow-ring @ badge.
 * Keeps "oleh @rahimam" intact in an accessible sr-only node so screen
 * readers announce the handle once without double-reading the glyph.
 */
export function AuthorByline({
  className = "",
  asLink = true,
}: {
  className?: string;
  asLink?: boolean;
}) {
  const inner = (
    <>
      <span className="ph-handle" aria-hidden="true">
        <span>oleh</span>
        <span className="ph-at">@</span>
        <span>rahimam</span>
      </span>
      <span className="sr-only">oleh @rahimam</span>
    </>
  );

  if (!asLink) {
    return <span className={className}>{inner}</span>;
  }

  return (
    <a
      href="https://www.threads.net/@rahimam"
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex min-h-tap items-center justify-center rounded-pill px-2 underline-offset-4 hover:underline ${className}`}
      aria-label="oleh @rahimam di Threads (buka dalam tab baharu)"
    >
      {inner}
    </a>
  );
}
