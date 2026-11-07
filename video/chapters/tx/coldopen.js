/* coldopen.js · the cold-open shot (approved in the style preview): MELISSA's real GOES-19 loop, AIFS's
   3-days-before track printed on top, the landfall miss as the payoff number. Used by 00 and the preview (90). */
const SAT = { x: 420, y: 0, s: 1080 };
function coldOpen(lt) {
  const G = satTrack(lt, 'MELISSA', SAT, { loop: 10 });
  satLegend(lt, G, 60);
  R.fade((lt - 2.2) / .3, () => R.mono(G.ref_kind === 'landfall' ? 'LANDFALL MISS' : 'MISS AT CLOSEST APPROACH', 1690, 420, 24, R.C.dim, 'center', 700));
  R.printLine(`${G.ref_error_km} km`, 1690, 500, 64, R.C.orange, (lt - 2.4) / .5, 'center');
  ctx.fillStyle = 'rgba(15,13,12,.85)'; ctx.fillRect(SAT.x, SAFE.b - 34, SAT.s, 44);
  R.src('NOAA GOES-19 ABI band 13 IR · track: ECMWF AIFS (archived run) vs IBTrACS', (lt - 1) / .5);
}
