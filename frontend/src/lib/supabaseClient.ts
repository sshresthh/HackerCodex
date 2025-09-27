import { env } from '$env/dynamic/public';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = env.PUBLIC_SUPABASE_URL;
const supabaseAnonKey = env.PUBLIC_SUPABASE_ANON_KEY;

let supabaseClient: SupabaseClient | null = null;

if (supabaseUrl && supabaseAnonKey) {
	supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
		auth: {
			persistSession: false,
			detectSessionInUrl: false
		}
	});
} else {
	console.warn('Supabase environment variables are missing. Map data will not load.');
}

export function getSupabaseClient(): SupabaseClient | null {
	return supabaseClient;
}

