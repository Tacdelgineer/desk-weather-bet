/* 01 · Title card (5 s), after the hook. */
shot(0, 'riso', 'title card', (lt) => {
  R.printLine('MY DESK AI', 960, 430, 120, R.C.white, lt / .5, 'center');
  R.fade((lt - .5) / .3, () => R.mono('vs', 960, 520, 40, R.C.dim, 'center', 800));
  R.printLine('THE WEATHER BETTING MARKET', 960, 640, 84, R.C.orange, (lt - .7) / .6, 'center');
}, { noCounter: true });
sfx(0, 'thunk', .5); sfx(.7, 'swish', .4);
