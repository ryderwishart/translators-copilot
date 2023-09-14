'use client';
import { useState } from 'react';
import DemoForm, { VerseData } from '@/components/DemoForm';
import SimilarVersesTable from '@/components/SimilarVersesTable';
import Chat from '@/components/Chat';
import PromptGenerator from '@/components/PromptGenerator';
import { QueryObject } from '@/lib/types';
import SourceVerse from '@/components/SourceVerse';

export default function Page() {

    const [searchCriteria, setSearchCriteria] = useState<string>('');
    const [sourceLanguageCode, setSourceLanguageCode] = useState<string>('');
    const [targetLanguageCode, setTargetLanguageCode] = useState<string>('');
    const [verseRef, setVerseRef] = useState<string>('');
    const [verseData, setVerseData] = useState<VerseData | undefined>();
    const [similarVerses, setSimilarVerses] = useState<QueryObject[] | undefined>();

    return (
        <div className="container space-y-8">
            <DemoForm
                setSearchCriteria={setSearchCriteria}
                setSourceLanguageCode={setSourceLanguageCode}
                setTargetLanguageCode={setTargetLanguageCode}
                setVerseRef={setVerseRef}
                setVerseData={setVerseData}
                setSimilarVerses={setSimilarVerses}
            />
            <SourceVerse verseRef={verseRef} verseData={verseData} />
            <SimilarVersesTable similarVerses={similarVerses} />
            <PromptGenerator
                similarVerses={similarVerses}
                sourceLanguageCode={sourceLanguageCode}
                targetLanguageCode={targetLanguageCode}
                sourceVerse={{
                    vref: verseData?.bsb.vref,
                    text: verseData?.bsb.content,
                    ...verseData
                }}
            />
            <Chat similarVerses={similarVerses} verseData={verseData} />
        </div>
    );
}
