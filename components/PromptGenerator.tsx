'use client';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/lib/types';
import { Button } from './ui/button';
import { useEffect, useState } from 'react';

interface Props {
    similarVerses: QueryObject[] | undefined;
    targetLanguageCode: string;
    sourceLanguageCode: string;
    sourceVerse: {
        vref: string | undefined;
        text: string | undefined;
        bsb?: {
            content: string;
            verse_number: number;
            vref: string;
        };
        macula?: {
            content: string;
            verse_number: number;
            vref: string;
        };
        target?: {
            content: string; // NOTE: may be available for reference, but will not be available for untranslated verses
            verse_number: number;
            vref: string;
        };
    };
}

export default function PromptGenerator(props: Props) {
    const prompt = generatePrompt(props);
    const [showCopiedText, setShowCopiedText] = useState<boolean>(false);

    // WE CAN EXPLORE WHAT IT MIGHT LOOK LIKE TO HAVE THE USER SELECT THE SPECIFIC EXAMPLES TO GENERATE THE PROMPT FROM
    // I.E. HAVING CHECKBOXES IN THE TABLE THAT WILL ADD THEM TO A LIST OF EXAMPLES TO INCLUDE IN THE PROMPT

    useEffect(() => {
        let id = setTimeout(() => {
            setShowCopiedText(false)
        }, 1000)

        return () => {
            clearTimeout(id);
        }
    }, [showCopiedText])

    if (!props.sourceVerse.vref) return null;
    
    return (
        <CollapsibleSection headerText="Prompt generator">
            <p>The following is a generated prompt that you can copy and paste into the chat below:</p>
            <div className="border-2 rounded-md p-4">
                <p>Translate the following sentence pairs into the target language:</p>
                <br />
                {props.similarVerses?.slice(0, 4).map((similarVerse) =>
                    similarVerse?.macula && similarVerse?.bsb && (
                        <div key={similarVerse.vref}>
                            <p>Greek/Hebrew Source: {similarVerse.macula}</p>
                            <p>English Source: {similarVerse.bsb}</p>
                            <p>Target ({props.targetLanguageCode}): {similarVerse.target}</p>
                            <br />
                        </div>
                    )
                )}
                <div>
                    <p>Deduce the target given the next sentence pair based on the above examples.</p>
                    <p>Greek/Hebrew Source: {props.sourceVerse.macula?.content}</p>
                    <p>English Source: {props.sourceVerse.bsb?.content}</p>
                    <p>Target ({props.targetLanguageCode}): </p>
                </div>
                <Button className="mt-4 w-[150px]" disabled={showCopiedText} onClick={() => {
                    setShowCopiedText(true);
                    copyTextToClipboard(prompt)
                }}>{showCopiedText ? "Copied!" : "Copy Prompt"}</Button>
            </div>
        </CollapsibleSection>
    )
}

const generatePrompt = (props: Props) => {
    const sourceVerseForPrompt = [
        `# Deduce the target given the next sentence pair based on the above examples.`,
        `### Greek/Hebrew Source: ${props.sourceVerse.macula?.content}`,
        `### English Source: ${props.sourceVerse.bsb?.content}`,
        `### Target (${props.targetLanguageCode}):`, // FIXME: add full target language name, not just the target language code
    ].join('\n');

    return (`# Translate the following sentence pairs into the target language:\n\n` +
        props.similarVerses?.slice(0, 4).map((similarVerse) =>
            `### Greek/Hebrew Source: ${similarVerse.macula}\n` +
            `### English Source: ${similarVerse.bsb}\n` +
            `### Target (${props.targetLanguageCode}): ${similarVerse.target}\n`,
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