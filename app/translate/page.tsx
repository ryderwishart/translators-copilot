'use client';
import PromptCompletion from '@/src/components/PromptCompletion';
import { useState, useEffect } from 'react';
import useSWR from 'swr';
import { SimilarExample } from '@/src/types';

async function fetcher(url: string) {
  const res = await fetch(url);

  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }

  return res.json();
}

export default function Page() {
  const [formInput, setFormInput] = useState(
    'default string so results initially populate',
  );
  const [input, setInput] = useState(
    'default string so results initially populate',
  );

  const [formLanguageCode, setFormLanguageCode] = useState('bsb_bible');
  const [sourceLanguageCode, setSourceLanguageCode] = useState('bsb_bible');

  const [formTargetLanguageCode, setFormTargetLanguageCode] = useState('aai');
  const [targetLanguageCode, setTargetLanguageCode] = useState('aai');

  const [formVerseRef, setFormVerseRef] = useState('ROM 1:1');
  const [verseRef, setVerseRef] = useState('ROM 1:1');

  const [similarSentences, setSimilarSentences] = useState<SimilarExample[]>(
    [],
  );

  const { data: sourceVerse, error: sourceVerseError }: any = useSWR(
    `http://localhost:3000/api/verse/${encodeURIComponent(
      verseRef,
    )}&${targetLanguageCode}`,
    fetcher,
  );

  const { data, error } = useSWR(
    `http://localhost:3000/api/query/${sourceLanguageCode}/${input}&limit=10`,
    fetcher,
  );

  useEffect(() => {
    if (data) {
      const fetchVerses = async () => {
        const updatedSentences: SimilarExample[] = await Promise.all(
          data.map(async (example: SimilarExample) => {
            const response = await fetch(
              `http://localhost:3000/api/verse/${encodeURIComponent(
                example.vref,
              )}&${targetLanguageCode}`,
            );
            const verseForExample = await response.json();
            console.log('>>>', { verseForExample });

            return {
              ...example,
              target: verseForExample.target.content,
              bsb: verseForExample.bsb.content,
              macula: verseForExample.macula.content,
            };
          }),
        );

        setSimilarSentences(updatedSentences);
      };

      fetchVerses();
    }
  }, [data, targetLanguageCode]);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (sourceVerseError) {
    return <div>Error: {sourceVerseError.message}</div>;
  }

  if (!sourceVerse) {
    return <div>Loading source verse...</div>;
  }

  if (error) return <div>Error: {error.message}</div>;
  if (!data) return <div>Loading similar sentences...</div>;

  // Once I have data, for each example in data, query the http://localhost:3000/api/verse/ endpoint for the example.vref and the target language code.
  // const similarSentences: Array<SimilarExample> = data.map((example: any) => {
  //   return {
  //     text: example.text,
  //     score: example.score,
  //     vref: example.vref,
  //     bsb: '', // verseForExample.bsb.content,
  //     macula: '', // verseForExample.macula.content,
  //   };
  // });

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h2 className="text-2xl font-bold">Translate</h2>
      <div className="flex flex-col items-center m-2">
        {/**
         * Here I need to construct the prompt using a template and the relevant fetched data.
         * 
         * promptData props looks like: 
         * promptData: {
    examples: SimilarExample[];
    targetLanguageCode: string;
    sourceLanguageCode: string;
    sourceVerse: {
        vref: string;
        text: string;
        macula: string;
        target?: string; // NOTE: may be available for reference, but will not be available for untranslated verses
    }
  }
         */}
        <PromptCompletion
          promptData={{
            examples: similarSentences,
            targetLanguageCode,
            sourceLanguageCode,
            sourceVerse,
          }}
        />
      </div>

      <div className="flex flex-col justify-between">
        <h2 className="text-2xl font-bold">
          Set input for translating, input language, and target language
        </h2>
        <form
          className="flex flex-row m-2 gap-1 min-w-max"
          onSubmit={(e) => {
            e.preventDefault();
            setInput(formInput);
          }}
        >
          <input
            className="bg-white shadow-lg mt-1 p-1 font-mono text-slate-400 w-11/12"
            type="text"
            value={formInput}
            onChange={(e) => setFormInput(e.target.value)}
          />
          <button className="bg-white rounded shadow-lg mt-1 p-1 uppercase text-sm bg-sky-300 hover:bg-sky-200">
            submit
          </button>
        </form>
        <div className="flex flex-row justify-between">
          {/** FIXME: need to populate form options using the /api/db_info endpoint */}
          <form
            className="flex flex-row m-2 gap-1"
            onSubmit={(e) => {
              e.preventDefault();
              setSourceLanguageCode(formLanguageCode);
            }}
          >
            <input
              className="bg-white shadow-lg mt-1 p-1 font-mono text-slate-400"
              type="text"
              value={formLanguageCode}
              onChange={(e) => setFormLanguageCode(e.target.value)}
            />
            <button className="bg-white rounded shadow-lg mt-1 p-1 uppercase text-sm bg-sky-300 hover:bg-sky-200">
              submit source language code
            </button>
          </form>
          <form
            className="flex flex-row m-2 gap-1"
            onSubmit={(e) => {
              e.preventDefault();
              setTargetLanguageCode(formTargetLanguageCode);
            }}
          >
            <input
              className="bg-white shadow-lg mt-1 p-1 font-mono text-slate-400"
              type="text"
              value={formTargetLanguageCode}
              onChange={(e) => setFormTargetLanguageCode(e.target.value)}
            />
            <button className="bg-white rounded shadow-lg mt-1 p-1 uppercase text-sm bg-sky-300 hover:bg-sky-200">
              submit target language code
            </button>
          </form>

          <form
            className="flex flex-row m-2 gap-1"
            onSubmit={(e) => {
              e.preventDefault();
              setVerseRef(formVerseRef);
            }}
          >
            <input
              className="bg-white shadow-lg mt-1 p-1 font-mono text-slate-400"
              type="text"
              value={formVerseRef}
              onChange={(e) => setFormVerseRef(e.target.value)}
            />
            <button className="bg-white rounded shadow-lg mt-1 p-1 uppercase text-sm bg-sky-300 hover:bg-sky-200">
              submit verse reference
            </button>
          </form>
        </div>
      </div>

      <div className="flex flex-col items-center m-2">
        <h2 className="text-2xl font-bold">
          Source Verse: {sourceVerse.bsb.vref}
        </h2>
        <div className="flex flex-col items-left">
          <div className="flex flex-row items-stretch m-2 gap-2">
            <h3 className="text-m font-bold">BSB</h3>
            <p>{sourceVerse.bsb.content}</p>
          </div>
          <div className="flex flex-row items-stretch m-2 gap-2">
            <h3 className="text-m font-bold">Macula</h3>
            <p>{sourceVerse.macula.content}</p>
          </div>
          <div className="flex flex-row items-stretch m-2 gap-2">
            <h3 className="text-m font-bold uppercase">{targetLanguageCode}</h3>
            <p>{sourceVerse.target.content}</p>
          </div>
        </div>
      </div>

      <h2 className="text-2xl font-bold">
        Most similar english verses to query string
      </h2>
      <div className="flex flex-col text-xs">
        <table className="table-auto w-full">
          <thead className="bg-gray-400">
            <tr>
              <th className="px-4 py-2">Reference</th>
              <th className="px-4 py-2">Target</th>
              <th className="px-4 py-2">English</th>
              <th className="px-4 py-2">Original language</th>
            </tr>
          </thead>
          <tbody>
            {similarSentences.map((example: SimilarExample) => (
              <tr
                key={example.vref}
                className="border-t border-gray-200 text-left"
              >
                <td className="px-4 py-2">{example.vref}</td>
                <td className="px-4 py-2">{example.target}</td>
                <td className="px-4 py-2">{example.bsb}</td>
                <td className="px-4 py-2">{example.macula}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
