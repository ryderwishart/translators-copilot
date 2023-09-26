'use client';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/lib/types';
import { Button } from './ui/button';
import { useEffect, useState } from 'react';
import { ChatRequestOptions, CreateMessage, Message } from 'ai';

interface Props {
    appendPromptToChat: (message: Message | CreateMessage, chatRequestOptions?: ChatRequestOptions | undefined) => Promise<string | null | undefined>;
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
    const [showMessageSent, setShowMessageSent] = useState<boolean>(false);

    // WE CAN EXPLORE WHAT IT MIGHT LOOK LIKE TO HAVE THE USER SELECT THE SPECIFIC EXAMPLES TO GENERATE THE PROMPT FROM
    // I.E. HAVING CHECKBOXES IN THE TABLE THAT WILL ADD THEM TO A LIST OF EXAMPLES TO INCLUDE IN THE PROMPT

    useEffect(() => {
        let id = setTimeout(() => {
            setShowMessageSent(false)
        }, 1000)

        return () => {
            clearTimeout(id);
        }
    }, [showMessageSent])

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
            <p>The following is a generated prompt based on the most similar verses that contains your provided search criteria. You can either send the message directly to chat, or you can copy-paste it yourself.</p>
            <div className="border-2 rounded-md p-4">
                <p>Translate the following sentence pairs into the target language:</p>
                <br />
                {props.similarVerses?.slice(0, 2).map((similarVerse) =>
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
                <div className="flex flex-row mt-4 gap-x-4">
                    <Button className="w-[150px]" disabled={showMessageSent} onClick={() => {
                        setShowMessageSent(true);
                        props.appendPromptToChat({
                            content: prompt,
                            role: 'user',
                        })
                        window.scrollTo(0, document.body.scrollHeight)
                    }}>
                        {showMessageSent ? "Sent!" : "Send to chat"}
                    </Button>
                    <Button className="w-[150px]" disabled={showCopiedText} onClick={() => {
                        setShowCopiedText(true);
                        copyTextToClipboard(prompt)
                    }}>
                        {showCopiedText ? "Copied!" : "Copy Prompt"}
                    </Button>
                </div>
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
        props.similarVerses?.slice(0, 2).map((similarVerse) =>
            `### Greek/Hebrew Source: ${similarVerse.macula}` +
            `### English Source: ${similarVerse.bsb}` +
            `### Target (${props.targetLanguageCode}): ${similarVerse.target}`,
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