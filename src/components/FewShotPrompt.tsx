'use client';

import { useCompletion } from 'ai/react';
import { type } from 'os';
import { useState, useEffect } from 'react';

interface Props {
  prompt: string;
}

function responseHandler(response: any) {
  console.log({ response });
}

export default function FewShotPrompt({ prompt }: Props) {
  const [translationComplete, setTranslationComplete] = useState(false);
  const [evaluationLineGroups, setEvaluationLineGroups] = useState<string[]>(
    prompt.split('\n\n').filter((_, lineGroupIndex) => lineGroupIndex !== 0),
  );
  const [evaluationPrompt, setEvaluationPrompt] = useState<string>('');
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
    syntheticEvent.target.value = prompt;
    handleInputChange(syntheticEvent as any);
  }, [prompt, handleInputChange]);

  // strip off the first and last quotation marks
  const renderedLineGroups = prompt
    .split('\n\n')
    .map((lineGroup, lineGroupIndex) => (
      <span key={lineGroupIndex} className="flex flex-col p-2 gap-1">
        {lineGroup.split('\n').map((line, lineIndex) =>
          line === 'Target:' ? null : line.startsWith('Target') ? (
            <span className="text-sky-600" key={lineIndex}>
              {line}
            </span>
          ) : (
            <span className="" key={lineIndex}>
              {line}
            </span>
          ),
        )}
      </span>
    ));

  const evaluationPrefix =
    'The following are translation pairs. One of them has been generated by AI. Please try to identify which of the following is incorrect:';

  useEffect(() => {
    if (translationComplete) {
      setEvaluationLineGroups((prevEvaluationLineGroups) => {
        // FIXME: let's just duplicate the array, then *display* the extra prefix and completion below, and then send a reordered complete prompt to the API
        const updatedEvaluationLineGroups = [
          evaluationPrefix,
          ...prevEvaluationLineGroups,
        ];
        updatedEvaluationLineGroups[updatedEvaluationLineGroups.length] = // NOTE: note -1 because I am adding a 0th item (the prefix)
          prevEvaluationLineGroups[prevEvaluationLineGroups.length - 1] +
          ' ' +
          completion;
        return updatedEvaluationLineGroups;
      });

      setEvaluationPrompt(
        evaluationLineGroups.sort(() => Math.random() - 0.5).join('\n\n'),
      );
    }
  }, [translationComplete, completion]);

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
            <div className="text-sky-600 mb-4 p-2">
              Target: <span className="text-orange-600">{completion}</span>
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
                  <button
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    disabled={isLoading || translationComplete}
                    type="submit"
                  >
                    {translationComplete ? (
                      <span className="">Translation generated!</span>
                    ) : isLoading ? (
                      <span className="">Generating translation...</span>
                    ) : (
                      <span className="">Generate translation</span>
                    )}
                  </button>
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
            {/* rendered evaluationLineGroups should show randomly sorted line groups */}
            {translationComplete ? (
              evaluationLineGroups
                .sort(() => Math.random() - 0.5)
                .map((lineGroup, lineGroupIndex) => (
                  <div key={lineGroupIndex} className="flex flex-col p-2 gap-1">
                    {lineGroup.split('\n').map((line, lineIndex) => (
                      <span key={lineIndex} className="">
                        {line.startsWith('Target') ? (
                          <span className="text-orange-600">{line}</span>
                        ) : (
                          <span className="">{line}</span>
                        )}
                      </span>
                    ))}
                  </div>
                ))
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
