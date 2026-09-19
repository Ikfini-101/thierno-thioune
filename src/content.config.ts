import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const publicationsCollection = defineCollection({
  loader: glob({ pattern: '**/*.md', base: "./src/content/publications" }),
  schema: () => z.object({
    title: z.string(),
    year: z.number(),
    authors: z.string(),
    journal: z.string(),
    volume: z.string(),
    citations: z.number().or(z.string()).optional(),
    link: z.string().optional(),
    theme: z.string().optional(),
    pdf: z.string().nullable().optional(),
  }),
});

export const collections = {
  'publications': publicationsCollection,
};