import React, { FormEvent, useState } from 'react';
import { ArrowUpRight, Check, LockKeyhole } from 'lucide-react';
import asset0 from './assets/soc-14-bg.png';

/**
 * A distinct "email gate" hypothesis for the Dark Studio announcement.
 * Instead of a single bottom CTA, the post behaves like a tactile editorial
 * sign-up card: the promise, date, and email capture are arranged as one
 * compact transmission panel.
 */
export function ComingSoonEmailGate() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (email.trim()) setSubmitted(true);
  };

  return (
    <main className="relative h-full w-full overflow-hidden bg-[#130d0d] text-[#f4eee7]">
      <img
        src={asset0}
        alt=""
        aria-hidden="true"
        className="absolute inset-0 h-full w-full object-cover opacity-35 mix-blend-screen"
      />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_15%,rgba(157,40,36,0.38),transparent_42%),linear-gradient(145deg,#171010_10%,rgba(20,12,12,0.74)_55%,#0b0808_100%)]" />
      <div className="absolute -right-20 top-44 h-72 w-72 rounded-full border border-[#d85445]/20" />
      <div className="absolute -right-7 top-57 h-56 w-56 rounded-full border border-[#d85445]/10" />

      <div className="relative z-10 flex h-full flex-col px-7 py-7">
        <header className="flex items-start justify-between border-b border-[#f4eee7]/20 pb-5">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-[#d85445]" />
              <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-[#d7bdb6]">
                Studio transmission
              </span>
            </div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#8f7772]">
              04 / 07 — private preview
            </p>
          </div>
          <span className="font-mono text-[10px] text-[#8f7772]">2024—25</span>
        </header>

        <section className="flex flex-1 flex-col justify-center py-10">
          <p className="mb-5 max-w-[250px] font-mono text-[11px] uppercase leading-[1.8] tracking-[0.18em] text-[#d85445]">
            A new body of work
            <br />
            arrives in 03 days
          </p>
          <h1 className="font-serif text-[76px] font-medium leading-[0.82] tracking-[-0.08em] text-[#f4eee7]">
            Don&apos;t
            <br />
            blink<span className="text-[#d85445]">.</span>
          </h1>
          <p className="mt-8 max-w-[250px] text-[15px] leading-[1.55] text-[#d8c9c4]">
            Three years of work, one collection. Get the first look before the
            doors open.
          </p>
        </section>

        <section className="border-t border-[#f4eee7]/20 pt-5">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#8f7772]">
                Access request
              </p>
              <h2 className="mt-1 text-[21px] font-medium tracking-[-0.03em]">
                Enter the room early
              </h2>
            </div>
            <span className="font-mono text-[10px] text-[#d85445]">01—01</span>
          </div>

          {submitted ? (
            <div className="flex min-h-[58px] items-center justify-between border border-[#d85445] bg-[#d85445]/10 px-4">
              <div className="flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#d85445] text-[#1a0c0c]">
                  <Check size={15} strokeWidth={2.5} />
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.12em]">
                  You&apos;re on the list
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSubmitted(false)}
                className="font-mono text-[10px] uppercase tracking-[0.15em] text-[#d7bdb6] underline underline-offset-4"
              >
                Change
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex border border-[#f4eee7]/35 bg-[#120b0b]/70 p-1">
              <label className="sr-only" htmlFor="studio-email">
                Your email address
              </label>
              <input
                id="studio-email"
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="your@email.com"
                className="min-w-0 flex-1 bg-transparent px-3 font-mono text-[12px] text-[#f4eee7] outline-none placeholder:text-[#8f7772]"
              />
              <button
                type="submit"
                aria-label="Request access"
                className="flex h-12 w-12 shrink-0 items-center justify-center bg-[#d85445] text-[#1a0c0c] transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0"
              >
                <ArrowUpRight size={19} />
              </button>
            </form>
          )}

          <div className="mt-4 flex items-center gap-2 text-[#8f7772]">
            <LockKeyhole size={11} />
            <span className="font-mono text-[9px] uppercase tracking-[0.1em]">
              One note only. No noise.
            </span>
          </div>
        </section>
      </div>
    </main>
  );
}
