import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'screens/translation_page.dart'; // make sure path is correct

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Civic Translator',
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool isLoading = false;

  Future<void> sendToBackend() async {
    setState(() {
      isLoading = true;
    });

    try {
      final response = await http.post(
        Uri.parse("http://10.0.2.2:5000/process"), // emulator URL
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "text": "This is a test sentence. This is second line."
        }),
      );

      final data = jsonDecode(response.body);

      List<String> lines = List<String>.from(data['lines']);
      List<String> audioFiles = List<String>.from(data['audio_files']);

      // 👉 NAVIGATION HERE
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TranslationPage(
            lines: lines,
            audioFiles: audioFiles,
          ),
        ),
      );
    } catch (e) {
      print("Error: $e");
    }

    setState(() {
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Civic Translator"),
      ),
      body: Center(
        child: isLoading
            ? const CircularProgressIndicator()
            : ElevatedButton(
                onPressed: sendToBackend,
                child: const Text("Translate"),
              ),
      ),
    );
  }
}
