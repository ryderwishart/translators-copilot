import FewShotPrompt from '@/src/components/FewShotPrompt';

interface DataProps {
  vref: string;
  target_language_code: string;
}

async function getData(props: DataProps): Promise<string> {
  const promptRes = await fetch(
    `http://localhost:3000/api/translation-prompt-builder?vref=${encodeURIComponent(
      props.vref,
    )}&target_language_code=${props.target_language_code}`,
  );

  if (!promptRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const promptString: string = await promptRes.json();

  // console.log({ promptString });
  return promptString;
}

export default async function Page() {
  const prompt = await getData({
    vref: 'ROM 1:6',
    target_language_code: 'aai',
  });

  return (
    <div className="flex flex-col items-center self-center">
      {prompt ? <FewShotPrompt prompt={prompt} /> : <div>Loading...</div>}
    </div>
  );
}
