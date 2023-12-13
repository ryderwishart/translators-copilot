import { url } from '@/app/config';
import { QueryObject } from '@/lib/types';
import { useEffect, useState } from 'react';


type Props = {
    input: string;
    sourceLanguageCode: string;
    limit?: number;
}

export default function useQuery({ sourceLanguageCode, input, limit }: Props) {

    const [queryData, setQueryData] = useState<QueryObject[] | null>(null);
    const [queryError, setQueryError] = useState<any>(null);

    useEffect(() => {
        if (sourceLanguageCode && input) {
            const fetchQuery = async () => {
                const response = await fetch(
                    `${url}/api/query/${sourceLanguageCode}/${input}&limit=${limit ? limit : 50}`,
                );
                if (!response.ok) {
                    setQueryError(response.statusText);
                } else {
                    const data: QueryObject[] = await response.json();
                    console.log(data);
                    setQueryData(data?.filter(item => (item.target && item.target !== '')));
                }
            }
            fetchQuery();
        }
    }, [sourceLanguageCode, input, limit]);

    return { queryData, queryError };
}

