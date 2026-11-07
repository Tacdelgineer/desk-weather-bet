/* 00 · Cold open (14 s). The approved satellite shot, then the storm miss and the question. The money result is
   kept for chapter 10 (owner, 2026-11-07). */
shot(0, 'riso', 'cold open: satellite + AI track', coldOpen, { noCounter: true });
shot(10, 'riso', 'the question', (lt) => {
  const G = window.GOES.MELISSA;
  R.mono(`HURRICANE ${G.storm} · AI FORECAST MADE ${G.days_before} DAYS BEFORE`, 960, 300, 28, R.C.dim, 'center', 800);
  R.printLine(`${G.ref_error_km} km off at landfall`, 960, 450, 96, R.C.white, lt / .4, 'center');
  R.printLine('can it beat the weather betting market?', 960, 640, 64, R.C.orange, (lt - 1) / .6, 'center');
  R.src('results/hurricanes.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(.6, 'whoosh', .35); sfx(2.4, 'thunk', .5); sfx(10, 'thunk', .5); sfx(11, 'swish', .4);
