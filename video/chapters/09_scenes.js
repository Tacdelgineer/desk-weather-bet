/* 09 · The bug — I almost went live with this (36 s). Scatter (riso), NWS vs bot (EVIDENCE), the v1 → v2 tags and the
   public issue's hashes (CRT, real captures), then two stat cards. */
shot(0, 'riso', 'the bug: extrapolation', bugShot, { noCounter: true });
shot(8, 'evidence', 'evidence: NWS vs bot', evNwsBot, { noCounter: true });

shot(14, 'crt', 'crt: rules tags + public hashes', (lt) => {
  const G = DATA.captures.git, I = DATA.captures.issue.filter(l => /^- v[12]/.test(l)), all = [...G.slice(0, 3), ...G.slice(G.indexOf(G.find(l => l.startsWith('$ git show rules-locked-v2:')))), ''];
  CR.statusBar('git · desk-weather-bet', 'REAL OUTPUT');
  let y = 52; all.forEach((l, k) => { const s = CR.typed(l, lt, .2 + k * .35, 70); if (s) CR.tx(s.slice(0, 96), 18, y + k * 16, 11, l.startsWith('$') ? CR.C.gh : CR.C.g); });
  if (lt > 3.6) { CR.tx('GitHub issue #1 · first comment · posted ' + DATA.captures.issue[0].replace('created_at: ', ''), 18, 170, 11, CR.C.amber);
    I.forEach((l, k) => { const s = l.replace(/\*\*|`/g, ''), m = s.match(/(v[12][^·]*)·[^·]*·[^·]*SHA-256 ([0-9a-f]{64})/); if (!m) return;
      CR.tx(m[1].trim().slice(0, 40), 18, 196 + k * 46, 12, k ? CR.C.gh : CR.C.gd, { wt: 700 });
      CR.tx(CR.typed(m[2], lt, 4 + k * .8, 60), 18, 214 + k * 46, 11, k ? CR.C.g : CR.C.gd); }); }
  if (lt > 6.2) CR.tx('v1 SUPERSEDED · v2 LOCKED BEFORE ANY REAL MONEY', 320, 330, 13, CR.C.gh, { wt: 700, align: 'center', inv: true });
}, { boot: true, noCounter: true });

shot(24, 'riso', 'stat card: bot vs NWS', (lt) => {
  const V = DATA.v1;
  R.mono(`PHOENIX · HIGH ON ${V.market_day} · v1 DRY RUN`, 960, 250, 28, R.C.dim, 'center', 800);
  R.arrowRow([`NWS ${V.nws}°F`, `BOT ${V.corrected.toFixed(1)}°F`], 960, 480, 120, [clamp(lt / .4), clamp((lt - .8) / .4)]);
  R.fade((lt - 1.8) / .4, () => R.mono(`"edge" ${V.pick.edge.toFixed(2)} at ${Math.round(V.pick.price * 100)}¢ · ${V.pick.side} "${V.pick.bracket}"`, 960, 640, 40, R.C.orange, 'center', 800));
  R.fade((lt - 2.8) / .4, () => R.mono(`the real high: ${V.cli}°F (NWS preliminary report)`, 960, 720, 30, R.C.white, 'center', 700));
  tag('PAPER MONEY', 1580, 92);
  R.src('results/evidence/v1-bug/summary.json', (lt - .5) / .5);
}, { noCounter: true });

shot(30, 'riso', 'stat card: v1 vs v2 TEST P&L', (lt) => {
  const A = DATA.v1v2.v1.aifs_cor_judge, B = DATA.v1v2.v2.aifs_cor_judge;
  R.mono('THE LIVE PLAYER (CORRECTED AIFS + JUDGE) · TEST WINDOW', 960, 250, 28, R.C.dim, 'center', 800);
  R.arrowRow([`v1 ${money(A.pnl)}`, `v2 ${money(B.pnl)}`], 960, 480, 110, [clamp(lt / .4), clamp((lt - .8) / .4)]);
  R.fade((lt - 1.8) / .4, () => R.mono(`${A.bets} bets → ${B.bets} bets`, 960, 600, 34, R.C.white, 'center', 700));
  R.fade((lt - 2.6) / .4, () => R.mono('v2 was designed after seeing these TEST days', 960, 680, 28, R.C.dim, 'center', 600));
  tag('PAPER MONEY', 1580, 92);
  R.src('results/v1_vs_v2.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(0, 'whoosh', .3); sfx(4.3, 'thunk', .6); sfx(8, 'paper', .5); sfx(11.1, 'thunk', .5); sfx(24, 'thunk', .5); sfx(24.8, 'thunk', .6); sfx(30, 'thunk', .5); sfx(30.8, 'thunk', .6);
