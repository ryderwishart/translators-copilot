import FewShotPrompt from '@/components/FewShotPrompt';

interface DataProps {
  vref: string;
  target_language_code: string;
}

export interface VerseData {
  source: string;
  reference: string;
  target: string;
}

export interface VerseDataMap {
  [vref: string]: VerseData;
}

async function getData(props: DataProps): Promise<VerseDataMap> {
  const promptRes = await fetch(
    `http://localhost:3000/api/translation-prompt-builder?vref=${encodeURIComponent(
      props.vref,
    )}&target_language_code=${props.target_language_code}`,
  );

  if (!promptRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const promptObject: VerseDataMap = await promptRes.json();

  console.log({ promptObject });
  return promptObject;
}

export default async function Page() {
  const prompt: VerseDataMap = await getData({
    vref: 'ROM 1:8',
    target_language_code: 'aai',
  });

  return (
    <div className="flex flex-col items-center self-center">
      {prompt ? <FewShotPrompt prompt={prompt} /> : <div>Loading...</div>}
    </div>
  );
}
