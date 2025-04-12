// app/privacy-policy.tsx
import React from 'react';
import { ScrollView, View, Text, Button } from 'react-native';
import { Link } from 'expo-router';
import { styles } from './_styles';

export default function PrivacyPolicy() {
  return (
    <ScrollView style={styles.container}>
      <View style={{ padding: 10 }}>
        <Text style={styles.header}>🤠 Privacy Policy – Ain’t Nobody Peekin’ in Yer Outhouse! 🚽</Text>
        <Text style={styles.subheader}>Last Updated: April 10, 2025 – ‘Cause We Ain’t Got Nothin’ Better to Do</Text>
        <Text style={styles.recipeContent}>
          Howdy, y’all! Welcome to Chuckle & Chow, where we rustle up recipes faster’n a coon dog chasin’ a possum. We ain’t here to snoop in yer britches or steal yer moonshine stash. This here’s how we keep yer secrets tighter’n a bullfrog’s behind:
        </Text>
        <Text style={styles.recipeSection}>🐷 What We Snag from Ya</Text>
        <Text style={styles.recipeContent}>
          We only grab what ya chuck at us—like them ingredients ya pick and maybe yer email if ya holler at us. Ain’t no fancy spy gear here, just a rusty ol’ keyboard and some hog grease.
        </Text>
        <Text style={styles.recipeSection}>🍺 How We Use Yer Loot</Text>
        <Text style={styles.recipeContent}>
          We sling yer picks into our recipe stewpot to whip up somethin’ tasty. Won’t sell yer info to no city slickers or telemarketer varmints—promise on Granny’s banjo!
        </Text>
        <Text style={styles.recipeSection}>🔫 Who Gets a Peek?</Text>
        <Text style={styles.recipeContent}>
          Nobody but us redneck coders and maybe Amazon when ya buy grub through our links. Them tax folks might come sniffin’ if the law hollers, but that’s it!
        </Text>
        <Text style={styles.recipeSection}>🍖 Keepin’ It Locked Up</Text>
        <Text style={styles.recipeContent}>
          We guard yer stuff like a coon guards its supper—ain’t no hackers gettin’ past our shotgun firewall. If they do, we’ll tan their hides!
        </Text>
        <Text style={styles.recipeSection}>🌽 Yer Rights, Pardner</Text>
        <Text style={styles.recipeContent}>
          Wanna see what we got on ya? Holler at bshoemak@mac.com and we’ll spill the beans. Tell us to ditch it, and it’s gone faster’n a pig in a mudslide.
        </Text>
        <Text style={styles.recipeContent}>
          Questions? Shoot us a line at bshoemak@mac.com—don’t reckon we’ll reply if the fish are bitin’, though!
        </Text>
        <View style={{ marginTop: 20 }}>
          <Link href="/" asChild>
            <Button title="🏠 Back Home, Y’all!" color="#FF4500" />
          </Link>
        </View>
      </View>
    </ScrollView>
  );
}