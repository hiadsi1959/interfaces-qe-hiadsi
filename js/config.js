/* Public HIADSI site settings */
window.HIADSI_CONFIG = {
  /**
   * Email to receive a notice for each download (via FormSubmit).
   * Example: "your.name@univ-usto.dz"
   * Leave empty to disable email (silent counters still work).
   */
  notificationEmail: "",

  /**
   * Silent counters (not shown on the public site).
   * View totals on compteurs.html (author access code).
   * Do not change counterNamespace after going live.
   */
  counterNamespace: "hiadsi1959-interfaces",
  counterApiBase: "https://countapi.mileshilliard.com/api/v1",

  /**
   * SHA-256 (hex) of the access code for compteurs.html.
   * Default code: hiadsi1959  — change by updating this hash.
   */
  statsAccessHash:
    "8da5f67a646696283c2d8ad3b745c885a2ad6f78a838a01b2e4c4409312e28c8",

  /**
   * Historical baseline (added to live CountAPI hits).
   * Keys must match data-interface ids in js/main.js.
   */
  baselineCounts: {
    "generation_inputs-QE": 10,
    "generation_pseudos": 10,
    "Interface-QE_v1": 10,
    "thermo_pw": 10,
    "supra-QE": 10,
    "QE-Alamode_interface": 10,
  },
};
