import { QueryObject } from "@/lib/types";
import CollapsibleSection from "./CollapsibleSection";
import { VerseData } from "./DemoForm";

type Props = {
    verseRef: string;
    verseData: VerseData | undefined;
}

export default function SourceVerse({ verseRef, verseData }: Props) {
    if (!verseRef || !verseData) return null;

    return (
        <CollapsibleSection headerText={`Source verse: ${verseRef}`}>
            <div className="flex flex-col">
                <div className="flex flex-row">
                    <p className="font-bold pr-2">English Reference:</p>
                    <p>{verseData.bsb.content}</p>
                </div>
                <div className="flex flex-row">
                    <p className="font-bold pr-2">Greek/Hebrew Source:</p>
                    <p>{verseData.macula.content}</p>
                </div>
                <div className="flex flex-row">
                    <p className="font-bold pr-2">Target:</p>
                    <p>{verseData.target.content}</p>
                </div>
            </div>
        </CollapsibleSection>
    )
}