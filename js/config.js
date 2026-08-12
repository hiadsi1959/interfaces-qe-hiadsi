/* Public HIADSI site settings */
window.HIADSI_CONFIG = {
  /**
   * Email to receive download notifications (via FormSubmit).
   * Example: "your.name@univ-usto.dz"
   * Leave empty to disable email (counters still work).
   */
  notificationEmail: "",

  /**
   * Public counters (no API key). CounterAPI v1 was shut down on 2026-08-07;
   * we now use CountAPI (mileshilliard) + optional baselines below.
   * Do not change counterNamespace after going live.
   */
  counterNamespace: "hiadsi1959-interfaces",
  counterApiBase: "https://countapi.mileshilliard.com/api/v1",

  /**
   * Historical downloads lost when CounterAPI v1 closed (add known totals here).
   * Displayed total = baseline + new CountAPI hits since migration.
   * Keys must match data-interface / IFACES ids in js/main.js.
   */
  baselineCounts: {
    "generation_inputs-QE": 0,
    "generation_pseudos": 0,
    "Interface-QE_v1": 0,
    "thermo_pw": 0,
    "supra-QE": 0,
    "QE-Alamode_interface": 0,
  },
};
