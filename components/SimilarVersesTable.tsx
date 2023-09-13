import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { QueryObject } from "@/hooks/UseQuery";
import CollapsibleSection from "./CollapsibleSection";

type Props = {
    similarVerses: QueryObject[] | null;
}

export default function SimilarVersesTable({ similarVerses }: Props) {
    if (!similarVerses) return null;

    return (
        <CollapsibleSection headerText="Similar Verses">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead className="w-[100px]">Reference</TableHead>
                        <TableHead>Target</TableHead>
                        <TableHead>English</TableHead>
                        <TableHead>Original language</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {similarVerses.map((similarVerse) => (
                        <TableRow key={similarVerse.vref}>
                            <TableCell className="font-medium">{similarVerse.vref}</TableCell>
                            <TableCell>{similarVerse.target}</TableCell>
                            <TableCell>{similarVerse.bsb}</TableCell>
                            <TableCell>{similarVerse.macula}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </CollapsibleSection>
    )
}