'use client';
// interface DataProps {
//   vref: string;
//   target_language_code: string;
// }
import React from 'react';

export interface AlignmentSet {
  vref: string;
  alignments: [Alignment];
}

export interface Alignment {
  source: string;
  target: string;
  bridge: string;
}

interface AlignmentTableProps {
  alignmentData: AlignmentSet[];
}

const AlignmentTable: React.FC<AlignmentTableProps> = ({ alignmentData }) => {
  return (
    <div className="flex flex-col items-center self-center bg-white shadow-md rounded-lg p-4 items-stretch">
      {/* {JSON.stringify(alignmentResponse)} */}
      {/** create a table to view alignments */}
      {alignmentData ? (
        alignmentData.map((alignmentSet: AlignmentSet) => (
          <div key={alignmentSet.vref} className="my-4">
            <div className="font-semibold text-lg mb-2">
              {alignmentSet.vref}
            </div>
            <table className="table-auto w-full">
              <thead>
                <tr className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
                  <th className="py-3 px-6 text-left w-1/3">Source</th>
                  <th className="py-3 px-6 text-left w-1/3">Bridge</th>
                  <th className="py-3 px-6 text-left w-1/3">Target</th>
                </tr>
              </thead>
              <tbody>
                {alignmentSet.alignments.map((alignment: Alignment) => (
                  <tr
                    key={alignment.source}
                    className="text-gray-600 text-sm font-light border-b border-gray-200"
                  >
                    <td className="py-3 px-6 w-1/3">{alignment.source}</td>
                    <td className="py-3 px-6 w-1/3">{alignment.bridge}</td>
                    <td className="py-3 px-6 w-1/3">{alignment.target}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      ) : (
        <div className="text-center py-4">Loading...</div>
      )}
    </div>
  );
};

async function getData(
  language_code: string,
  n: number,
): Promise<AlignmentSet[]> {
  const promptRes = await fetch(
    `http://localhost:3000/api/get_alignment?language_code=${language_code}&n=${n}`,
    {
      next: { revalidate: 10 },
    },
  );

  if (!promptRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const alignmentArray = await promptRes.json();

  console.log({ alignmentArray });
  return alignmentArray;
}

export default function Page() {
  const [alignmentData, setAlignmentData] = React.useState<AlignmentSet[]>([]);
  const [url, setUrl] = React.useState(
    'http://localhost:3000/api/get_alignment',
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const data = await getData('spapddpt_split', 10);
    setAlignmentData(data);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          URL:
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </label>
        <input type="submit" value="Submit" />
      </form>
      <AlignmentTable alignmentData={alignmentData} />
    </div>
  );
}
