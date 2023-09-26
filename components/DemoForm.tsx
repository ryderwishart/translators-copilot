'use client';
import { Dispatch, SetStateAction} from 'react';
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useForm } from 'react-hook-form';
import LanguageDropdown from '@/components/LanguageDropdown';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/lib/types';

const formSchema = z.object({
    searchCriteria: z.string({
        required_error: "Please enter search criteria.",
    }),
    sourceLanguageCode: z.string({
        required_error: "Please select a language.",
    }),
    targetLanguageCode: z.string({
        required_error: "Please select a language.",
    }),
    verseRef: z.string({
        required_error: "Please enter a valid verse reference.",
    }),
})

export type VerseData = {
    bsb: {
        verse_number: number;
        vref: string;
        content: string;
    },
    macula: {
        verse_number: number;
        vref: string;
        content: string;
    },
    target: {
        verse_number: number;
        vref: string;
        content: string;
    },
}

type Props = {
    setVerseData: Dispatch<SetStateAction<VerseData | undefined>>;
    setSimilarVerses: Dispatch<SetStateAction<QueryObject[] | undefined>>;
    setSearchCriteria: Dispatch<SetStateAction<string>>;
    setSourceLanguageCode: Dispatch<SetStateAction<string>>;
    setTargetLanguageCode: Dispatch<SetStateAction<string>>;
    setVerseRef: Dispatch<SetStateAction<string>>;
}

export default function DemoForm({
    setVerseData,
    setSimilarVerses,
    setSearchCriteria,
    setSourceLanguageCode,
    setTargetLanguageCode,
    setVerseRef,
}: Props) {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        reValidateMode: "onSubmit",
    })

    function onSubmit(values: z.infer<typeof formSchema>) {
        const {
            sourceLanguageCode,
            targetLanguageCode,
            verseRef,
            searchCriteria
        } = values;

        setSearchCriteria(searchCriteria)
        setSourceLanguageCode(sourceLanguageCode)
        setTargetLanguageCode(targetLanguageCode)
        setVerseRef(verseRef)

        const fetchQuery = async () => {
            const verseResponse = await fetch(
                `http://localhost:3000/api/verse/${encodeURIComponent(
                    verseRef,
                )}&${targetLanguageCode}`,
            );
            const verseData = await verseResponse.json();
            setVerseData(verseData ? verseData : undefined);

            const queryResponse = await fetch(
                `http://localhost:3000/api/query/${sourceLanguageCode}/${searchCriteria}&limit=50`,
            );
            const queryData = await queryResponse.json();
            if (queryData) {
                const fetchVerses = async () => {
                    const updatedVerses: QueryObject[] = await Promise.all(
                        queryData.map(async (example: QueryObject) => {
                            const response = await fetch(
                                `http://localhost:3000/api/verse/${encodeURIComponent(
                                    example.vref,
                                )}&${targetLanguageCode}`,
                            );
                            const verseForExample = await response.json();
                            const verseHasTarget = verseForExample.target.content !== '';
                            return verseHasTarget ? {
                                ...example,
                                target: verseForExample.target.content,
                                bsb: verseForExample.bsb.content,
                                macula: verseForExample.macula.content,
                            } : null;
                        }),
                    );

                    // Once we get here, we have an array of all similar verses, with null items where there were no targets
                    // so we need to filter out the null items
                    const examplesWithTargets = updatedVerses.filter(x => x !== null);
                    setSimilarVerses(examplesWithTargets);
                };

                fetchVerses();
            }
        }

        fetchQuery();
    }

    return (
        <CollapsibleSection headerText="Search" preventCollapse>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="border-2 rounded-md p-4 space-y-6">
                    <FormField
                        control={form.control}
                        name="searchCriteria"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Search</FormLabel>
                                <FormControl>
                                    <Input placeholder="Search criteria here..." {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="verseRef"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Verse Reference</FormLabel>
                                <FormControl>
                                    <Input placeholder="ROM 1:1" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <div className="flex md:flex-row flex-col justify-start">
                        <div className="w-full md:w-1/2">
                            <FormField
                                control={form.control}
                                name="sourceLanguageCode"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Source language</FormLabel>
                                        <LanguageDropdown onValueChange={field.onChange} />
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="w-full mt-4 md:mt-0 md:w-1/2">
                            <FormField
                                control={form.control}
                                name="targetLanguageCode"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Target language</FormLabel>
                                        <LanguageDropdown onValueChange={field.onChange} />
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                    <FormDescription>
                        If no languages are shown, follow the steps to populate the database.
                    </FormDescription>
                    <Button type="submit">Search</Button>
                </form>
            </Form>
        </CollapsibleSection>
    )
}
