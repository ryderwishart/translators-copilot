import { useEffect, useState } from 'react';
import useQuery from './UseQuery';
import { QueryObject } from "@/lib/types";

type Props = {
    input: string;
    sourceLanguageCode: string;
    targetLanguageCode: string;
    limit?: number;
}

type SimilarVersesOutput = { similarVerses: QueryObject[] | null };

export default function useSimilarVerses({ sourceLanguageCode, targetLanguageCode, input, limit }: Props): SimilarVersesOutput {
    const [similarVerses, setSimilarVerses] = useState<QueryObject[]>([]);

    const { queryData, queryError } = useQuery({ sourceLanguageCode, input, limit });

    useEffect(() => {
        if (queryError) {
            console.error('Error fetching similar verses', queryError);
            setSimilarVerses([]);
        } else if (queryData) {
            const fetchVerses = async () => {
                const updatedVerses: QueryObject[] = await Promise.all(
                    queryData.map(async (example: QueryObject) => {
                        const response = await fetch(
                            `http://localhost:3000/api/verse/${encodeURIComponent(
                                example.vref,
                            )}&${targetLanguageCode}`,
                        );
                        const verseForExample = await response.json();
                        console.log('>>>', { verseForExample });

                        return {
                            ...example,
                            target: verseForExample.target.content,
                            bsb: verseForExample.bsb.content,
                            macula: verseForExample.macula.content,
                        };
                    }),
                );

                setSimilarVerses(updatedVerses);
            };

            fetchVerses();
        }
    }, [queryData, queryError, targetLanguageCode]);

    return (!sourceLanguageCode || !targetLanguageCode || !input)
        ? { similarVerses: null }
        : { similarVerses };
}

