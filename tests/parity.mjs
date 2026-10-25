// Runs templates/tuner/engine.js on the settings given as JSON on stdin and
// prints the palettes as JSON. Used by test_parity.py.
import { readFileSync } from "node:fs";
import vm from "node:vm";

const ctx = {};
vm.createContext(ctx);
vm.runInContext(readFileSync(new URL("../templates/tuner/engine.js", import.meta.url), "utf8"), ctx);
const cases = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(cases.map(s => ctx.LambdaEngine.buildPalette(s))));
