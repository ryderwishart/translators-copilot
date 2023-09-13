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

type Props = {
    setSearchCriteria: Dispatch<SetStateAction<string>>;
    setSourceLanguageCode: Dispatch<SetStateAction<string>>;
    setTargetLanguageCode: Dispatch<SetStateAction<string>>;
    setVerseRef: Dispatch<SetStateAction<string>>;
}

export default function DemoForm({ setSearchCriteria, setSourceLanguageCode, setTargetLanguageCode, setVerseRef }: Props) {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
    })

    function onSubmit(values: z.infer<typeof formSchema>) {
        setSearchCriteria(values.searchCriteria)
        setSourceLanguageCode(values.sourceLanguageCode)
        setTargetLanguageCode(values.targetLanguageCode)
        setVerseRef(values.verseRef)
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
