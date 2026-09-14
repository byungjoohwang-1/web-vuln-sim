(function (root, factory) {
  'use strict';
  const evaluator = factory();
  if (typeof module === 'object' && module.exports) module.exports = evaluator;
  else root.SecurityLabEvaluator = evaluator;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const scalar = value => value == null ? '' : String(value).trim().toLowerCase();
  const tokens = value => (Array.isArray(value) ? value : String(value || '').split(/[,\s]+/)).map(scalar).filter(Boolean);
  function checkRule(check, answers) {
    const value = answers[check.controlId];
    if (check.type === 'composite' || check.ruleGroup === 'composite') {
      return Array.isArray(check.conditions) && check.conditions.length > 0 && check.conditions.every(rule => checkRule(rule, answers));
    }
    if (check.mustBeInRange || check.minValue != null || check.maxValue != null) {
      if (value == null || scalar(value) === '') return false;
      const number = Number(value);
      const min = check.mustBeInRange ? check.mustBeInRange.min : check.minValue;
      const max = check.mustBeInRange ? check.mustBeInRange.max : check.maxValue;
      return Number.isFinite(number) && (min == null || number >= min) && (max == null || number <= max);
    }
    if (check.ruleGroup === 'mustContainAtLeastOneOf' || check.mustContainAtLeastOneOf) {
      const selected = tokens(value);
      return tokens(check.mustContainAtLeastOneOf).some(item => selected.includes(item)) && !tokens(check.mustNotContain).some(item => selected.includes(item));
    }
    if (check.ruleGroup === 'mustDisallowAll') return !tokens(check.disallowItems).some(item => tokens(value).includes(item));
    if (check.mustBe !== undefined) return scalar(value) === scalar(check.mustBe);
    return false;
  }
  function evaluate(lesson, answers, quizSelection) {
    const rules = lesson.checks.map(check => Object.assign({}, (lesson.expectedTextRules || []).find(rule => rule.controlId === check.controlId) || {}, check));
    // Supplemental rules describe the same controls, not additional scored checks.
    const checkResults = rules.map(rule => ({id:rule.id,label:rule.label,controlId:rule.controlId,required:!!rule.required,points:Number(rule.points || 0),pass:checkRule(rule, answers)}));
    const configScore = checkResults.reduce((sum, check) => sum + (check.pass ? check.points : 0), 0);
    const configMax = checkResults.reduce((sum, check) => sum + check.points, 0);
    const quizCorrect = Number.isInteger(quizSelection) && quizSelection === lesson.quiz.correctOptionIndex;
    const allRequiredPassed = checkResults.every(check => !check.required || check.pass);
    return {checkResults,configScore,configMax,quizCorrect,allRequiredPassed,totalScore:configScore + (quizCorrect ? 20 : 0),maxScore:configMax + 20,mastered:allRequiredPassed && quizCorrect,attemptsAt:new Date().toISOString()};
  }
  return {evaluate,checkRule};
});
