/* 08 · The judge (30 s, PAPER MONEY): three real decisions the decision model made, then judge vs the one-line rule. */
function judgeCard(i) {
  return (lt) => {
    const E = DATA.judge.examples[i], S = E.state, cut = DATA.judge.cutoff;
    CR.statusBar(`DECISION MODEL · STRANDS DECIDER 2B · ${E.ticker}`, `${i + 1} / ${DATA.judge.examples.length}`);
    const lines = [`city            ${S.city}`, `market          ${S.market}`, `bet side        ${S.bet_side} at $${S.price_to_pay.toFixed(2)}`,
      `forecast        ${S.forecast_high_F}°F  ± ${S.forecast_error_sd_F}`, `model says      ${S.bet_side} wins ${Math.round(S.model_probability_side_wins * 100)}%`,
      `model edge      ${S.model_edge}`, `spread          ${S.bid_ask_spread}`];
    lines.forEach((l, k) => { const s = CR.typed(l, lt, .2 + k * .25, 60); if (s) CR.tx(s, 30, 70 + k * 22, 14, CR.C.g); });
    if (lt > 2.2) { const p = clamp((lt - 2.2) / .8), v = E.p_bet * p;
      CR.tx('P(bet)', 30, 252, 14, CR.C.gh, { wt: 700 }); CR.tx(CR.bar(v, 30), 100, 252, 14, v > cut ? CR.C.gh : CR.C.g); CR.tx(v.toFixed(3), 420, 252, 14, CR.C.gh, { wt: 700 });
      const cx = 100 + 30 * cut * 8.4; CR.tx('|', cx, 268, 14, CR.C.amber); CR.tx(`bets only above ${cut}`, cx - 50, 286, 10, CR.C.amber); }
    if (lt > 3.4) CR.tx(`JUDGE: ${E.judge_action.toUpperCase()}   RULE: ${E.rule_action.toUpperCase()}`, 320, 318, 16, CR.C.gh, { wt: 700, align: 'center', inv: true });
    if (lt > 4.2) CR.tx(`${E.judge_action === 'bet' ? 'the bet' : 'if it had bet'}: ${E.won ? 'won' : 'lost'} ${money(E.pnl)}`, 320, 342, 12, E.won ? CR.C.g : CR.C.orange, { align: 'center' });
  };
}
[0, 1, 2].forEach(i => shot(i * 5, 'crt', `judge example ${i + 1}`, judgeCard(i), { boot: i === 0, noCounter: true }));

shot(15, 'riso', 'judge vs one-line rule (PAPER MONEY)', (lt) => {
  const J = DATA.judge, rows = [['judge (decision model)', J.judge, R.C.orange], ['one-line rule', J.rule, R.C.white]];
  head(lt, 'THE JUDGE vs THE ONE-LINE RULE', `same corrected forecasts, TEST window · judge bets if P(bet) > ${J.cutoff}, rule if edge > ${J.rule_threshold}`);
  rows.forEach(([name, r, col], i) => { const x = 200 + i * 800, p = (lt - .5 - i * .6) / .4;
    R.fade(p, () => { R.panel(x, 260, 700, 560); R.mono(name, x + 350, 340, 30, col, 'center', 800);
      R.mono(`${r.bets} bets · won ${Math.round(r.win_rate * 100)}%`, x + 350, 640, 28, R.C.white, 'center', 700);
      R.mono(`fees $${r.fees.toFixed(2)}`, x + 350, 700, 24, R.C.dim, 'center', 600); });
    R.printLine(money(r.pnl), x + 350, 530, 110, col, p - .5, 'center'); });
  R.fade((lt - 3) / .4, () => R.mono('the judge loses less — about break-even, not proof of an edge', 960, 920, 30, R.C.orange, 'center', 800));
  tag('PAPER MONEY', 1580, 92);
  R.src('results/judge.json · results/judge_examples.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(15, 'whoosh', .3); sfx(16, 'thunk', .5); sfx(16.6, 'thunk', .5);
