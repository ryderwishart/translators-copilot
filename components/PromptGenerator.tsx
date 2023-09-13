'use client';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/hooks/UseQuery';
import { Button } from './ui/button';

interface Props {
    similarVerses: QueryObject[];
    targetLanguageCode: string;
    sourceLanguageCode: string;
    sourceVerse: {
        vref: string;
        text: string;
        bsb: {
            content: string;
        };
        macula: {
            content: string;
        };
        target?: {
            content: string; // NOTE: may be available for reference, but will not be available for untranslated verses
        };
    };
}

export default function PromptGenerator(props: Props) {
    const prompt = generatePrompt(props);
    console.log(prompt);
    return (
        <CollapsibleSection headerText="Prompt Generator">
            <p>The following is a generated prompt that you can copy and paste into the chat below:</p>
            <div className="border-2 rounded-md p-4">
                <p>Translate the following sentence pairs into the target language:</p>
                <br />
                {props.similarVerses?.slice(0, 2).map((similarVerse) =>
                    similarVerse?.macula && similarVerse?.bsb && (
                        <div key={similarVerse.vref}>
                            <p>Greek/Hebrew Source: {similarVerse.macula}</p>
                            <p>English Reference: {similarVerse.bsb}</p>
                            <p>Target: {similarVerse.target}</p>
                            <br />
                        </div>
                    )
                )}
                <div>
                    <p>Greek/Hebrew Source: {props.sourceVerse.macula.content}</p>
                    <p>English Reference: {props.sourceVerse.bsb.content}</p>
                    <p>Target:</p>
                </div>
                <Button className="mt-4" onClick={() => copyTextToClipboard(prompt)}>Copy Prompt</Button>
            </div>
        </CollapsibleSection>
    )
}

const generatePrompt = (props: Props) => {
    const sourceVerseForPrompt = [
        `Greek/Hebrew Source: ${props.sourceVerse.macula.content}`,
        `English Reference: ${props.sourceVerse.bsb.content}`,
        `Target:`, // FIXME: add full target language name, not just the target language code
    ].join('\n');

    return (`Translate the following sentence pairs into the target language:\n\n` +
        props.similarVerses?.slice(0, 2).map((similarVerse) =>
            `Greek/Hebrew Source: ${similarVerse.macula}\n` +
            `English Reference: ${similarVerse.bsb}\n` +
            `Target: ${similarVerse.target}\n`,
        ).join('\n') + '\n\n' + sourceVerseForPrompt
    )

    /** prompt should look like this:
     * Translate the following sentence pairs into {targetLanguageCode}:
     *
     * Greek/Hebrew Source: {example1.macula}
     * English Reference: {example1.english}
     * Target {targetLanguageCode}: {example1.target}
     *
     * ...etc. for each example in props.promptData.examples
     *
     * Greek/Hebrew Source: {sourceVerse.macula}
     * English Reference: {sourceVerse.english}
     * Target {targetLanguageCode}:
     *
     */
}

async function copyTextToClipboard(text: string) {
    if ('clipboard' in navigator) {
        return await navigator.clipboard.writeText(text);
    }
}