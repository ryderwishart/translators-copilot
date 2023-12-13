import { url } from '@/app/config';
import { useEffect, useState } from 'react';

type VerseData = {
    bsb: VerseObject,
    macula: VerseObject,
    target: VerseObject,
}

type VerseObject = {
    verse_number: number;
    vref: string;
    content: string;
}

type Props = {
    verseRef: string;
    targetLanguageCode: string;
}

export default function useVerse({ verseRef, targetLanguageCode }: Props) {

    const [verseData, setVerseData] = useState<VerseData | null>(null);
    const [verseError, setVerseError] = useState<any>(null);

    useEffect(() => {
        if (targetLanguageCode && verseRef) {
            const fetchQuery = async () => {
                const response = await fetch(
                    `${url}/api/verse/${encodeURIComponent(
                        verseRef,
                    )}&${targetLanguageCode}`,
                );
                if (!response.ok) {
                    setVerseError(response.statusText);
                } else {
                    const data: VerseData = await response.json();
                    console.log(data);
                    setVerseData(data);
                }
            }
            fetchQuery();
        }
    }, [targetLanguageCode, verseRef]);

    return { verseData, verseError };
}

