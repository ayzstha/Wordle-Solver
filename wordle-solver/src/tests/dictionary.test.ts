import { Dictionary } from '../lib/dictionary';

describe('Dictionary', () => {
    let dictionary: Dictionary;

    beforeAll(() => {
        dictionary = new Dictionary();
        dictionary.loadWords('data/words.txt');
    });

    test('should load words correctly', () => {
        expect(dictionary.getWords().length).toBeGreaterThan(0);
    });

    test('should validate a known word', () => {
        expect(dictionary.isWordValid('apple')).toBe(true);
    });

    test('should invalidate an unknown word', () => {
        expect(dictionary.isWordValid('unknownword')).toBe(false);
    });
});