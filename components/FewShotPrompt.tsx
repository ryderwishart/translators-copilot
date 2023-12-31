'use client';

import { useCompletion } from 'ai/react';
import { type } from 'os';
import { useState, useEffect } from 'react';
import { VerseDataMap, VerseData } from '@/app/translate/page';

interface Props {
  prompt: VerseDataMap;
}

interface FormattedVerseData {
  'Greek/Hebrew Source': string;
  'English Reference': string;
  Target: string;
}

function responseHandler(response: any) {
  console.log({ response });
}

export default function FewShotPrompt({ prompt }: Props) {
  console.log('in few shot prompt:', { prompt });

  const [translationComplete, setTranslationComplete] = useState(false);
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [promptString, setPromptString] = useState('');

  const {
    completion,
    input,
    stop,
    isLoading,
    handleInputChange,
    handleSubmit,
  } = useCompletion({
    api: '/api/completion',
    onResponse: responseHandler,
    onFinish: () => {
      setTranslationComplete(true);
    },
  });

  useEffect(() => {
    const syntheticEvent = {
      target: document.createElement('input'),
    };

    const promptExamples = Object.values(prompt).map(
      (lineGroup: VerseData): FormattedVerseData => ({
        'Greek/Hebrew Source': lineGroup['source'],
        'English Reference': lineGroup['reference'],
        Target: lineGroup['target'],
      }),
    );
    // console.log({ promptExamples });

    const effectPromptString: string =
      'Translate each of the following source sentences into the target language:\n' +
      promptExamples
        .map((example: FormattedVerseData) => {
          return `Source: ${example['Greek/Hebrew Source']}\nEnglish: ${example['English Reference']}\nTarget: ${example['Target']}`;
        })
        .join('\n\n');
    console.log({ promptString });
    syntheticEvent.target.value = effectPromptString;
    setPromptString(effectPromptString);
    handleInputChange(syntheticEvent as any);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [prompt, handleInputChange]);

  // strip off the first and last quotation marks
  const renderedLineGroups = Object.keys(prompt).map(
    (key: string, lineGroupIndex) => (
      <span key={lineGroupIndex} className="flex flex-col p-2 gap-1">
        {key}
        {Object.keys(prompt[key]).map((lineKey, lineIndex) =>
          lineKey.startsWith('Target') ? (
            prompt[key][lineKey] === '' ? null : (
              <span className="text-sky-600 flex" key={lineIndex}>
                <span className="basis-1/4">{lineKey}</span>{' '}
                <span className="flex basis-3/4">{prompt[key][lineKey]}</span>
              </span>
            )
          ) : (
            <span className="flex" key={lineIndex}>
              <span className="text-slate-600 basis-1/4">{lineKey}</span>{' '}
              <span className="flex basis-3/4">{prompt[key][lineKey]}</span>
            </span>
          ),
        )}
      </span>
    ),
  );

  return (
    <main className="bg-gray-100 min-h-screen pt-12 md:pt-20 pb-6 px-20 md:px-0">
      <div className="max-w-6xl mx-auto p-3">
        <h1 className="text-6xl font-bold mb-2 text-gray-700">
          Few Shot Prompt
        </h1>
        <p className="text-xl text-gray-700">
          Generate a translation using few-shot example translation pairs most
          relevant to the verse-to-translate, then evaluate using a second pass
          through the large language model.
        </p>
        <div className="flex flex-row gap-3">
          <div className="p-4 rounded bg-slate-200 m-5 text-xs w-1/2">
            {renderedLineGroups}
            <div className="flex text-sky-600 mb-4 p-2">
              <span className="basis-1/4">Target</span>{' '}
              <span className="flex basis-3/4 text-orange-600">
                {completion}
              </span>
            </div>

            <div data-aria-label="Forward translation" className="">
              <form className="m-2" onSubmit={(e) => handleSubmit(e)}>
                <label className="block text-orange-600 text-sm font-bold mb-2 hidden">
                  <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    value={input}
                    onChange={(e) =>
                      handleInputChange({
                        ...e,
                        target: { ...e.target, value: prompt },
                      })
                    }
                  />
                </label>
                <div className="flex space-x-4 text-sm">
                  <div className="relative">
                    <button
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                      disabled={isLoading || translationComplete}
                      type="submit"
                      onMouseEnter={() => setTooltipVisible(true)}
                      onMouseLeave={() => setTooltipVisible(false)}
                    >
                      {translationComplete ? (
                        <span className="">Translation generated!</span>
                      ) : isLoading ? (
                        <span className="">Generating translation...</span>
                      ) : (
                        <span className="">Generate translation</span>
                      )}
                    </button>
                    {tooltipVisible && (
                      <div className="absolute z-10 w-64 p-2 mb-12 text-sm text-white bg-blue-500 rounded shadow-lg">
                        {promptString}
                      </div>
                    )}
                  </div>

                  <button
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    type="button"
                    onClick={stop}
                  >
                    Interrupt
                  </button>
                </div>
              </form>
            </div>
          </div>
          <div
            data-aria-label="Evaluation"
            className="p-4 rounded bg-slate-200 m-5 text-xs w-1/2"
          >
            {/* rendered evaluationLineGroups should show randomly sorted line
            groups */}
            {translationComplete ? (
              <p>Translation complete. Ready for evaluation.</p>
            ) : (
              <p>
                Once you generate a forward translation, it can be evaluated
                here.
              </p>
            )}
            <div className="">
              <form className="m-2">
                <label className="block text-orange-600 text-sm font-bold mb-2 hidden">
                  <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    value={input}
                    onChange={(e) =>
                      handleInputChange({
                        ...e,
                        target: { ...e.target, value: prompt },
                      })
                    }
                  />
                </label>
                <div className="flex space-x-4 text-sm"></div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
