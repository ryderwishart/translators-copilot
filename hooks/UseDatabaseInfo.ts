import useSWR from 'swr';
import { swrFetcher } from '@/lib/utils';
import { url } from '@/app/config';

type DatabaseInfoResponse = {
    data: DatabaseInfoItem[];
    error: any;
}

type DatabaseInfoItem = {
    name: string;
    columns: string[];
    num_rows: number;
}

export default function useDatabaseInfo() {

    const { data, error }: DatabaseInfoResponse = useSWR(
        `${url}/api/db_info`,
        swrFetcher,
    );

    return { data, error };
}