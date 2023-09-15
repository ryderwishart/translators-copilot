import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import CollapsibleSection from "./CollapsibleSection";
import { Separator } from "./ui/separator";

export interface AlignmentSet {
    vref: string;
    alignments: Alignment[];
}

export interface Alignment {
    source: string;
    target: string;
    bridge: string;
}

type Props = {
    alignmentData: AlignmentSet[];
}

export default function AlignmentTable({ alignmentData }: Props) {
    return (
        <CollapsibleSection headerText="Similar verses based on search criteria">
            {alignmentData ? (
                alignmentData.map((alignmentSet: AlignmentSet, idx) => (
                    <div key={idx}>
                        
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[100px] font-bold">{alignmentSet.vref}</TableHead>
                                    <TableHead>Source</TableHead>
                                    <TableHead>Target</TableHead>
                                    <TableHead>Bridge</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {alignmentSet.alignments.map((alignment, idx) => (
                                    <TableRow key={idx}>
                                        <TableCell></TableCell>
                                        <TableCell>{alignment.source}</TableCell>
                                        <TableCell>{alignment.target}</TableCell>
                                        <TableCell>{alignment.bridge}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                        <Separator />
                    </div>
                ))
            ) : (
                <div>Loading...</div>
            )}
        </CollapsibleSection>
    )
}

const dummyData = [
    {
        vref: "Gen 1:1",
        alignments: [
            {
                source: "In the beginning",
                target: "In the beginning",
                bridge: "In the beginning",
            },
            {
                source: "God created",
                target: "God created",
                bridge: "God created",
            },
            {
                source: "the heavens and the earth.",
                target: "the heavens and the earth.",
                bridge: "the heavens and the earth.",
            },
        ],
    },
    {
        vref: "Gen 1:2",
        alignments: [
            {
                source: "The earth was without form and void, and darkness was over the face of the deep.",
                target: "The earth was without form and void, and darkness was over the face of the deep.",
                bridge: "The earth was without form and void, and darkness was over the face of the deep.",
            },
        ]
    }
];