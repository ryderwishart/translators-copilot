'use client';
import { useState } from 'react';
import DemoForm from '@/components/DemoForm';
import PromptCompletion from '@/components/PromptCompletion';
import SimilarVersesTable from '@/components/SimilarVersesTable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useSimilarVerses from '@/hooks/UseSimilarVerses';
import useVerse from '@/hooks/UseVerse';
import Chat from '@/components/Chat';
import PromptGenerator from '@/components/PromptGenerator';

export default function Page() {

    const [searchCriteria, setSearchCriteria] = useState<string>('');
    const [sourceLanguageCode, setSourceLanguageCode] = useState<string>('');
    const [targetLanguageCode, setTargetLanguageCode] = useState<string>('');
    const [verseRef, setVerseRef] = useState<string>('');

    const { verseData, verseError } = useVerse({ verseRef: verseRef, targetLanguageCode})

    const { similarVerses } = useSimilarVerses({
        sourceLanguageCode,
        targetLanguageCode,
        input: searchCriteria
    });

    return (
        <div className="container space-y-8">
            <DemoForm
                setSearchCriteria={setSearchCriteria}
                setSourceLanguageCode={setSourceLanguageCode}
                setTargetLanguageCode={setTargetLanguageCode}
                setVerseRef={setVerseRef}
            />
            <SimilarVersesTable similarVerses={similarVerses} />
            {similarVerses && verseData && (
                <PromptGenerator
                    similarVerses={similarVerses}
                    sourceLanguageCode={sourceLanguageCode}
                    targetLanguageCode={targetLanguageCode}
                    sourceVerse={{
                        vref: verseData.bsb.vref,
                        text: verseData.bsb.content,
                        ...verseData
                    }}
                />
            )}
            <Chat />
        </div>
    );
}
