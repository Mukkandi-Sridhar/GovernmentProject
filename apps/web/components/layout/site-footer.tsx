export function SiteFooter() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-6 text-sm text-slate-600 sm:px-6 lg:px-8">
        <p>Andhra Pradesh Welfare AI Platform</p>
        <div className="flex gap-4">
          <a className="hover:text-slateText" href="#" aria-label="Terms">
            Terms
          </a>
          <a className="hover:text-slateText" href="#" aria-label="Privacy">
            Privacy
          </a>
          <a className="hover:text-slateText" href="#" aria-label="Version">
            Version 1.0.0
          </a>
          <a className="hover:text-slateText" href="#" aria-label="Contact">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}

