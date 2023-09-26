export type FewShotTranslationPromptExample = {
    reference: string;
    hypothesis?: string;
    transliteration?: string;
    alternate_references?: Array<String>;
};

export type FewShotTranslationPrompt = {
    promptTemplate: string; // Note: string template that accepts source, examples, prefix, suffix?
    examples: Array<FewShotTranslationPromptExample>;
};

export interface SimilarExample {
    text: string;
    score: number;
    vref: string;
    target?: string;
    bsb?: string;
    macula?: string;
    transliteration?: string;
}

export interface QueryObject {
    text: string;
    score: number;
    vref: string;
    target?: string;
    bsb?: string;
    macula?: string;
    transliteration?: string;
}