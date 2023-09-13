'use client';

import { useChat } from 'ai/react';
import { QueryObject } from '@/hooks/UseQuery';

interface Props {
  promptData: {
    examples: QueryObject[];
    targetLanguageCode: string;
    sourceLanguageCode: string;
    sourceVerse: {
      vref: string;
      text: string;
      bsb: {
        content: string;
      };
      macula: {
        content: string;
      };
      target?: {
        content: string; // NOTE: may be available for reference, but will not be available for untranslated verses
      };
    };
  };
}

export default function PromptCompletion(props: Props) {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  const prompt = generatePrompt(props);

  return (
    <div className="mx-auto w-full flex flex-col stretch">
      {/* <div
        id="prompt-display"
        className="flex flex-col items-center justify-center text-sm bg-gray-100 rounded shadow-lg p-8 max-w-xl overflow-x-auto"
      >
        <div className="whitespace-pre-wrap">{prompt}</div>
      </div> */}

      {messages.map((m) => (
        <div key={m.id}>
          {m.role === 'user' ? 'User: ' : 'AI: '}
          {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <label>
          Submit this prompt? (hit any key in input box to populate input)
          <input
            className="w-full bottom-0 border border-gray-300 rounded mb-8 shadow-xl p-2 h-max m-2"
            value={input}
            defaultValue={prompt}
            onChange={(e) => {
              console.log('submitting');

              handleInputChange({
                ...e,
                target: {
                  ...e.target,
                  value: prompt,
                },
              });
            }}
          />
        </label>
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

const generatePrompt = (props: Props) => {
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
  const { promptData } = props;

  const sourceVerseForPrompt = [
    `Greek/Hebrew Source: ${promptData.sourceVerse.macula.content}`,
    `English Reference: ${promptData.sourceVerse.bsb.content}`,
    `Target:`, // FIXME: add full target language name, not just the target language code
  ].join('\n');

  return (`Translate the following sentence pairs into the target language:\n\n` +
    promptData.examples?.slice(0, 2).map((example) =>
      `Greek/Hebrew Source: ${example.macula}\n` +
      `English Reference: ${example.bsb}\n` +
      `Target: ${example.target}\n`,
    ).join('\n') + '\n\n' + sourceVerseForPrompt
  )
}