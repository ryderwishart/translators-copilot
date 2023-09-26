import { VerseData } from '@/components/DemoForm';
import { QueryObject } from '@/lib/types';
import { useEffect, useState } from 'react';

type Props = {
    similarVerses: QueryObject[] | undefined;
    verseData: VerseData | undefined;
}

export default function useTargetTokens({ similarVerses, verseData }: Props) {

    const [availableTokens, setAvailableTokens] = useState<string[] | undefined>(undefined);

    useEffect(() => {
        if (similarVerses && verseData) {
            let allTokens: string[] = [];

            for (let i = 0; i < similarVerses.length; i++) {
                const target = similarVerses[i].target;
                if (!target) continue;
                const targetTokens = target.split(' ');
                for (let j = 0; j < targetTokens.length; j++) {
                    allTokens.push(getStrippedToken(targetTokens[j]));
                }
            }

            const verseDataTokens = verseData.target.content.split(' ');
            for (let i = 0; i < verseDataTokens.length; i++) {
                allTokens.push(verseDataTokens[i]);
            }

            const allAvailableTokens = Array.from(new Set(generateAvailableTokens(allTokens)));
            setAvailableTokens(allAvailableTokens);
        }
    }, [similarVerses, verseData]);

    return { availableTokens };
}

export const generateAvailableTokens = (allTokens: string[] | undefined) => {
    if (!allTokens) return undefined;
    const strippedTokens = allTokens.map(token => getStrippedToken(token))
    const sortedAvailableTokens = strippedTokens.sort((a, b) => a.localeCompare(b))
    return sortedAvailableTokens;
}

export const getStrippedToken = (token: string) => {
    let strippedToken = token.toLowerCase();
    const punctuation = ['.', ',', ';', ':', '!', '?', '(', ')', '[', ']', '{', '}', '"', "'", "“", "”"];
    token.split('').forEach(char => {
        if (punctuation.includes(char)) {
            strippedToken = strippedToken.replace(char, '');
        }
    });
    return strippedToken;
}