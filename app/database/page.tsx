import { DatabaseInfo } from '@/components/DatabaseTable';

interface Table {
  name: string;
  columns: string[];
  num_rows: number;
  rows: string[];
}

async function getData(): Promise<{ dbInfo: Table[] }> {
  const dbInfoRes = await fetch('http://localhost:3000/api/db_info');

  if (!dbInfoRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const dbInfo: Table[] = await dbInfoRes.json();

  /**
   * DB info looks like this on the api endpoint:
   * [{"name":"bsb_bible","columns":["vref","text","vector"],"num_rows":10},{"name":"txq","columns":["vref","text","vector"],"num_rows":9490},{"name":"abx","columns":["vref","text","vector"],"num_rows":7940},{"name":"macula","columns":["vref","text","vector"],"num_rows":10},{"name":"aby","columns":["vref","text","vector"],"num_rows":7957},{"name":"aak","columns":["vref","text","vector"],"num_rows":7957},{"name":"aai","columns":["vref","text","vector"],"num_rows":7957}]
   *
   * I want to query one string for each name/language code and append each result to its respective table in the dbInfo array
   */

  const sampleQueryString = 'this is a test query string';

  for (const table of dbInfo) {
    table.rows = []; // Need to add a `rows` property to each table object in dbInfo
    const queryRes = await fetch(
      `http://localhost:3000/api/query/${table.name}/${sampleQueryString}&limit=10`,
    );
    if (!queryRes.ok) {
      throw new Error(
        `Failed to fetch data for ${table.name}. Error: ${queryRes.statusText}`,
      );
    }
    const queryData = await queryRes.json();
    const firstNonEmptyResult = queryData.find((result: any) => result.text);
    if (firstNonEmptyResult) {
      table.rows.push(firstNonEmptyResult.text);
    }
  }

  return {
    dbInfo,
  };
}

export default async function Page() {
  const data = await getData();

  return (
    <main>
      {data ? <DatabaseInfo dbInfo={data.dbInfo} /> : <div>Loading...</div>}
    </main>
  );
}
