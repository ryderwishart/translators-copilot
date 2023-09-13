import useSWR from 'swr';
import { swrFetcher } from '@/lib/utils';

type QueryResponse = {
    data: QueryObject[];
    error: any;
}

export type QueryObject = {
    text: string;
    score: number;
    vref: string;
    target?: string;
    bsb?: string;
    macula?: string;
    transliteration?: string;
}

type Props = {
    input: string;
    sourceLanguageCode: string;
    limit?: number;
}

export default function useQuery({ sourceLanguageCode, input, limit }: Props) {

    const { data: queryData, error: queryError }: QueryResponse = useSWR(
        `http://localhost:3000/api/query/${sourceLanguageCode}/${input}&limit=${limit ? limit : 10}`,
        swrFetcher,
    );

    return (!sourceLanguageCode || !input)
        ? { queryData: null, queryError: null }
        : { queryData, queryError };
}

