import { useState } from 'react';

const BIBTEX = `@article{rudebench2026,
  title={RudeBench: A Multi-Dimensional Behavioral Benchmark for Evaluating LLM Resilience Under Hostile Prompting Conditions},
  author={[Author Names]},
  year={2026},
  url={https://rudebench.com},
  note={Preprint}
}`;

export default function BibTeXCopy() {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(BIBTEX);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = BIBTEX;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-[var(--color-surface-2)]">
        <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">BibTeX</span>
        <button
          onClick={handleCopy}
          className="text-xs px-2.5 py-1 rounded bg-[var(--color-surface-3)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <pre className="p-4 text-sm text-[var(--color-text-secondary)] overflow-x-auto font-mono">
        {BIBTEX}
      </pre>
    </div>
  );
}
