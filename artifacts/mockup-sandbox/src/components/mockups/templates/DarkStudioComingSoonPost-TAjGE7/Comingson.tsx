import './fonts.css';
import asset0 from "./assets/soc-14-bg.png";

import React from 'react';
import { ArrowRight } from 'lucide-react';

export function ComingSoon() {
  return (
    <div
      style={{ width: "100%", height: "100%" }}
      className="relative overflow-hidden bg-black flex flex-col items-center text-white"
    >
      {/* Background Image & Overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src={asset0}
          alt="Abstract Background"
          className="w-full h-full object-cover opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent"></div>
        <div className="absolute inset-0 bg-black/20 mix-blend-multiply"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-between h-full py-20 w-full px-12 text-center">
        
        {/* Top */}
        <div className="flex flex-col items-center space-y-4 pt-10">
          <div className="w-8 h-8 rounded-full border border-red-500/50 flex items-center justify-center">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          </div>
          <div className="tracking-[0.4em] text-xs uppercase text-zinc-400 font-['Space_Mono']">
            Project No. 04
          </div>
        </div>

        {/* Middle */}
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

        {/* Bottom */}
        <div className="space-y-12 w-full flex flex-col items-center pb-8">
          <div className="w-[1px] h-16 bg-gradient-to-b from-red-500 to-transparent"></div>
          
          <button className="flex items-center gap-3 border-b border-white/30 pb-2 hover:border-white transition-colors duration-500 group">
            <span className="font-['Space_Mono'] text-sm tracking-[0.2em] uppercase">Join the list</span>
            <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform duration-500" />
          </button>
        </div>
      </div>
    </div>
  );
}
