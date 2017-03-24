import { Member } from './member';
import { Card } from './card';
import { CardReview } from './review';


export class Requirement {
    id: number;
    code: string;
    name: string;
    description: string;
    other_comments: string;
    cards: Card[];
    value: number;
    estimated_number_of_hours: number;
    active: number;
    spent_time: number;
    percentage_of_completion: number;
}