import { Solver } from '../lib/solver';

describe('Solver', () => {
    let solver: Solver;

    beforeEach(() => {
        solver = new Solver();
    });

    test('findPossibleWords should return correct words based on constraints', () => {
        const guesses = [
            { word: 'crane', result: 'green' }, // Example guess with result
            { word: 'slate', result: 'yellow' } // Example guess with result
        ];
        const possibleWords = solver.findPossibleWords(guesses);
        expect(possibleWords).toContain('crate'); // Example expected word
        expect(possibleWords).toContain('trace'); // Example expected word
    });

    test('findPossibleWords should return an empty array if no words match', () => {
        const guesses = [
            { word: 'apple', result: 'red' } // Example guess with result
        ];
        const possibleWords = solver.findPossibleWords(guesses);
        expect(possibleWords).toHaveLength(0);
    });

    // Additional tests can be added here
});