import useSWR from 'swr';
import { swrFetcher } from '@/lib/utils';

type VerseResponse = {
    data: {
        bsb: VerseObject,
        macula: VerseObject,
        target: VerseObject,
    }
    error: any;
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

    const { data: verseData, error: verseError }: VerseResponse = useSWR(
        `http://localhost:3000/api/verse/${encodeURIComponent(
            verseRef,
        )}&${targetLanguageCode}`,
        swrFetcher,
    );

    return (!verseRef || !targetLanguageCode)
        ? { verseData: null, verseError: null }
        : { verseData, verseError };
}

