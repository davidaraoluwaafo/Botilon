import './fonts.css';
import asset0 from "./assets/soc-14-bg.png";

import React from 'react';
import { ArrowRight } from 'lucide-react';

/**
 * Filled CTA variant of the Dark Studio coming-soon post.
 * The original composition is intentionally retained; only the bottom action
 * is given a stronger, more tactile tap target.
 */
export function ComingSoonFilledCTA() {
  return (
    <div
      style={{ width: "100%", height: "100%" }}
      className="relative overflow-hidden bg-black flex flex-col items-center text-white"
    >
      <div className="absolute inset-0 z-0">
        <img
          src={asset0}
          alt="Abstract Background"
          className="w-full h-full object-cover opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent"></div>
        <div className="absolute inset-0 bg-black/20 mix-blend-multiply"></div>
      </div>

      <div className="relative z-10 flex flex-col items-center justify-between h-full py-20 w-full px-12 text-center">
        <div className="flex flex-col items-center space-y-4 pt-10">
          <div className="w-8 h-8 rounded-full border border-red-500/50 flex items-center justify-center">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          </div>
          <div className="tracking-[0.4em] text-xs uppercase text-zinc-400 font-['Space_Mono']">
            Project No. 04
          </div>
        </div>

        <div className="space-y-8 transform -translate-y-8">
          <h1 className="text-8xl font-medium tracking-tighter leading-[0.9] font-['Playfair_Display']">
            Coming
            <br />
            <span className="text-red-500">Soon</span>
          </h1>
          <p className="text-zinc-300 font-light tracking-wide text-lg max-w-[280px] mx-auto leading-relaxed">
            Three years of work, one collection. The new studio drops this Friday.
          </p>
        </div>

        <div className="space-y-12 w-full flex flex-col items-center pb-8">
          <div className="w-[1px] h-16 bg-gradient-to-b from-red-500 to-transparent"></div>

          <div className="flex flex-col items-center">
            <button
              type="button"
              aria-label="Join the list"
              className="group relative flex h-[52px] w-[320px] items-center justify-center gap-3 rounded-full bg-red-500 text-white shadow-[0_8px_14px_rgba(0,0,0,0.52),inset_0_1px_0_rgba(255,255,255,0.28)] transition-transform duration-500 hover:-translate-y-0.5 active:translate-y-0"
            >
              <span className="font-['Space_Mono'] text-base tracking-[0.2em] uppercase">
                Join the list
              </span>
              <ArrowRight className="h-4 w-4 transform transition-transform duration-500 group-hover:translate-x-1" />
            </button>
            <div aria-hidden="true" className="mt-10 h-px w-[320px] bg-white/30" />
          </div>
        </div>
      </div>
    </div>
  );
}
