/* Historical core recordings do not establish optional full-workflow checks. */
const EvidenceStatus = {
  rule(rule, fired, rules) {
    if (rule === fired) return 'decided';
    if (['receiver', 'readers_disagree', 'audit', 'invisible_text'].includes(rule)) return 'not evaluated in this run';
    const i = rules.indexOf(rule), stop = rules.indexOf(fired);
    return stop < 0 ? 'no recorded status' : i < stop ? 'no stop recorded (core)' : 'not reached';
  },
  cross(c) {
    const x = c.cross;
    if (!x || x.count != null) return '';
    if (c.gate.rule === 'mismatch' && Number.isInteger(c.gate.quantity) && c.gate.quantity === x.agreed && x.sam_only > 0 && !x.spark_only && !x.doubled) {
      return `Strict visualization count unavailable. The recorded gate accepted ${c.gate.quantity} matched cartons; its confidence policy tolerates doubtful SAM-only detections. This does not add them to the count. The receipt was blocked because the note quantity differs.`;
    }
    return 'No single agreed count in this visualization; the recorded gate decision is shown separately.';
  }
};
